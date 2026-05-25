import argparse
import re
import boto3
from datetime import datetime


YYYYMM_RE = re.compile(r"^\d{6}$")


def human_readable(size_bytes: int) -> str:
    gb = size_bytes / (1024 ** 3)
    tb = size_bytes / (1024 ** 4)
    if tb >= 1:
        return f"{tb:.2f} TB"
    return f"{gb:.2f} GB"


def iter_month_range(start_yyyymm: str, end_yyyymm: str):
    start = datetime.strptime(start_yyyymm, "%Y%m")
    end = datetime.strptime(end_yyyymm, "%Y%m")
    if start > end:
        raise ValueError("start month must be <= end month")
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        yield f"{year:04d}{month:02d}"
        month += 1
        if month > 12:
            month = 1
            year += 1


def list_subfolders(s3, bucket: str, prefix: str) -> list[str]:
    """Return immediate subfolder names (without the parent prefix, no trailing slash)."""
    paginator = s3.get_paginator("list_objects_v2")
    names = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter="/"):
        for cp in page.get("CommonPrefixes", []) or []:
            full = cp["Prefix"]
            name = full[len(prefix):].rstrip("/")
            if name:
                names.append(name)
    return names


def sum_prefix_size(s3, bucket: str, prefix: str) -> tuple[int, int]:
    paginator = s3.get_paginator("list_objects_v2")
    total_size = 0
    total_objects = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []) or []:
            total_size += obj["Size"]
            total_objects += 1
    return total_size, total_objects


def normalize_prefix(bucket: str, prefix: str) -> str:
    p = prefix.lstrip("/")
    # If the user accidentally included the bucket name at the start, strip it.
    if p.startswith(f"{bucket}/"):
        p = p[len(bucket) + 1:]
    if p and not p.endswith("/"):
        p += "/"
    return p


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute the size of S3 folders under a given prefix, "
                    "aggregating monthly subfolders in YYYYMM format."
    )
    parser.add_argument("--bucket", required=True, help="S3 bucket name (e.g. ccc2-cdrs)")
    parser.add_argument("--region", default="us-east-1", help="AWS region (default: us-east-1)")
    parser.add_argument("--prefix", default="monthly/",
                        help="Base prefix inside the bucket (default: monthly/). "
                             "Do NOT include the bucket name.")
    parser.add_argument("--start", default="202501", help="Start month YYYYMM (inclusive)")
    parser.add_argument("--end", default="202604", help="End month YYYYMM (inclusive)")
    parser.add_argument("--profile", default=None, help="Optional AWS profile name")
    parser.add_argument("--verbose", action="store_true",
                        help="Print size per month for each folder")
    return parser


def main():
    args = build_parser().parse_args()
    prefix = normalize_prefix(args.bucket, args.prefix)
    requested_months = list(iter_month_range(args.start, args.end))
    requested_set = set(requested_months)

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    s3 = session.client("s3", region_name=args.region)

    print(f"Bucket : {args.bucket}")
    print(f"Region : {args.region}")
    print(f"Prefix : {prefix}")
    print(f"Range  : {args.start} .. {args.end}  ({len(requested_months)} months)")
    print("-" * 78)

    top_folders = list_subfolders(s3, args.bucket, prefix)
    if not top_folders:
        print(f"No folders found under s3://{args.bucket}/{prefix}")
        return

    grand_total = 0
    grand_objects = 0
    folders_without_yyyymm = []

    for folder_name in top_folders:
        folder_prefix = f"{prefix}{folder_name}/"
        subfolders = list_subfolders(s3, args.bucket, folder_prefix)
        yyyymm_present = [s for s in subfolders if YYYYMM_RE.match(s)]

        if not yyyymm_present:
            folders_without_yyyymm.append(folder_name)
            print(f"{folder_name:<45} {'--':>12}  (no YYYYMM subfolders)")
            continue

        in_range = sorted(set(yyyymm_present) & requested_set)
        missing = sorted(requested_set - set(yyyymm_present))

        folder_total = 0
        folder_objects = 0
        per_month = []

        for yyyymm in in_range:
            month_prefix = f"{folder_prefix}{yyyymm}/"
            size, count = sum_prefix_size(s3, args.bucket, month_prefix)
            folder_total += size
            folder_objects += count
            per_month.append((yyyymm, size, count))

        grand_total += folder_total
        grand_objects += folder_objects

        note = ""
        if not in_range:
            note = "  (no YYYYMM in requested range)"
        print(f"{folder_name:<45} {human_readable(folder_total):>12}  "
              f"({folder_objects} objects, {len(in_range)}/{len(requested_months)} months){note}")

        if args.verbose:
            for yyyymm, size, count in per_month:
                print(f"    {yyyymm}  {human_readable(size):>12}  ({count} objects)")
            if missing:
                print(f"    missing in range: {', '.join(missing)}")

    print("-" * 78)
    print(f"{'TOTAL':<45} {human_readable(grand_total):>12}  "
          f"({grand_objects} objects)")

    if folders_without_yyyymm:
        print()
        print("Folders with NO YYYYMM-style subfolders:")
        for name in folders_without_yyyymm:
            print(f"  - {name}")


if __name__ == "__main__":
    main()
