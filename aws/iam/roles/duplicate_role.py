import boto3
import json

def duplicar_iam_role(nombre_rol_origen, nombre_rol_destino):
    """
    Duplica un rol de AWS IAM, incluyendo su política de confianza,
    políticas administradas adjuntas y políticas en línea incrustadas.
    """
    iam = boto3.client('iam')
    print(f"Iniciando duplicación del rol '{nombre_rol_origen}' a '{nombre_rol_destino}'...")

    # --- 1. OBTENER INFORMACIÓN DEL ROL DE ORIGEN ---
    try:
        # Obtener la política de confianza (Trust Policy)
        response_role = iam.get_role(RoleName=nombre_rol_origen)
        trust_policy = response_role['Role']['AssumeRolePolicyDocument']
        print(f"  > Política de confianza obtenida.")

        # Obtener las políticas administradas adjuntas (Managed Policies)
        attached_policies = iam.list_attached_role_policies(RoleName=nombre_rol_origen)['AttachedPolicies']
        print(f"  > {len(attached_policies)} políticas administradas adjuntas encontradas.")

        # Obtener las políticas en línea (Inline Policies)
        inline_policy_names = iam.list_role_policies(RoleName=nombre_rol_origen)['PolicyNames']
        inline_policies = []
        for name in inline_policy_names:
            policy_doc = iam.get_role_policy(RoleName=nombre_rol_origen, PolicyName=name)['PolicyDocument']
            inline_policies.append({'PolicyName': name, 'PolicyDocument': policy_doc})
        print(f"  > {len(inline_policies)} políticas en línea encontradas.")

    except iam.exceptions.NoSuchEntityException:
        print(f"\n Error: El rol de origen '{nombre_rol_origen}' no existe.")
        return
    except Exception as e:
        print(f"\n Error al obtener información del rol: {e}")
        return

    # --- 2. CREAR EL NUEVO ROL (Rol Destino) ---
    try:
        # La política de confianza debe serializarse a string para create_role
        trust_policy_json = json.dumps(trust_policy)

        print(f"  > trust_policy_json '{trust_policy_json}'...")
        
        iam.create_role(
            RoleName=nombre_rol_destino,
            AssumeRolePolicyDocument=trust_policy_json
        )
        print(f"\n Rol '{nombre_rol_destino}' creado exitosamente con la política de confianza.")

    except iam.exceptions.EntityAlreadyExistsException:
        print(f"\n Error: El rol de destino '{nombre_rol_destino}' ya existe. Intenta con otro nombre.")
        return
    except Exception as e:
        print(f"\n Error al crear el rol: {e}")
        return

    # --- 3. ADJUNTAR LAS POLÍTICAS ADMINISTRADAS ---
    for policy in attached_policies:
        try:
            iam.attach_role_policy(
                RoleName=nombre_rol_destino,
                PolicyArn=policy['PolicyArn']
            )
            print(f"  > Adjuntada política administrada: {policy['PolicyArn']}")
        except Exception as e:
            print(f"  Advertencia: No se pudo adjuntar {policy['PolicyArn']}. Error: {e}")

    # --- 4. AÑADIR LAS POLÍTICAS EN LÍNEA ---
    for inline_policy in inline_policies:
        try:
            # La política en línea debe serializarse a string
            policy_document_json = json.dumps(inline_policy['PolicyDocument'])
            
            iam.put_role_policy(
                RoleName=nombre_rol_destino,
                PolicyName=inline_policy['PolicyName'],
                PolicyDocument=policy_document_json
            )
            print(f"  > Creada política en línea: {inline_policy['PolicyName']}")
        except Exception as e:
            print(f"  Advertencia: No se pudo crear la política en línea {inline_policy['PolicyName']}. Error: {e}")
            
    print(f"\n ¡Duplicación de rol finalizada con éxito!")


# El nombre del rol que deseas copiar
ROL_ORIGEN = 'hn-be-mcp-server-conceptgroups-task-role-dev' 
# El nombre que tendrá el nuevo rol
ROL_DESTINO = 'hn-be-edgar-load-logs-task-role-prod' 

# Asegúrate de tener tus credenciales de AWS configuradas correctamente (perfil, variables de entorno, etc.)
# y los permisos necesarios para realizar estas operaciones (IAM Full Access).
# ¡Advertencia! Los nombres de los roles son *case-insensitive* y deben ser únicos.

duplicar_iam_role(ROL_ORIGEN, ROL_DESTINO)