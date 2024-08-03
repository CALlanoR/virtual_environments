def validate_client(new_function=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if "client" in kwargs:
                print("Before decorating...")
                result = func(*args,
                              **kwargs)
                print("After decorating")
                return result
            else:
                client = 10
                featureFlagInClientJson = False
                providerGroupFacilitiesFeatureFlag = True
                if featureFlagInClientJson:
                    if providerGroupFacilitiesFeatureFlag:
                        print("Before decorating")
                        result = new_function(*args,
                                              **kwargs,
                                              client=client)
                        print("After decorating")
                        return result
                print("Before decorating")
                result = func(*args,
                              **kwargs,
                              client=client)
                print("After decorating")
                return result
        return wrapper
    return decorator

@validate_client()
def service2(name,
             client=None):
    return f"Hello in service2, {name}! - client: {client}"

@validate_client(service2)
def service(name,
            client=None):
    return f"Hello in service, {name}! - client: {client}"

result1 = service("Alice")
print(result1)

