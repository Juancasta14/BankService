# FEATURE_SPEC_002_autenticacion.md -- Inicio de sesión

## Bloque 1. Objetivo y precondiciones
- **Actor:** Usuario registrado en el sistema.
- **Objetivo:** Autenticarse para obtener un token JWT que le permita interactuar con los endpoints protegidos.
- **Precondiciones:**
  - El usuario debe existir previamente en el `UserRepository` con un hash criptográfico de contraseña válido.

## Bloque 2. Entrada
```json
{
  "username": "juan_doe",
  "password": "mypassword123"
}
```

## Bloque 3. Flujo principal
1. El caso de uso (`LoginService`) consulta el repositorio por el `username` dado.
2. Si el usuario no existe, arroja inmediatamente el error de credenciales inválidas.
3. Si existe, delega al `PasswordHasher` (puerto) la comparación de la contraseña ingresada en texto plano contra el hash guardado.
4. Si las credenciales coinciden, delega al `TokenService` (puerto) la creación del payload y la firma del token JWT.
5. Retorna el string del JWT generado.

## Bloque 4. Errores de dominio
- `InvalidCredentials`: Excepción unificada que se arroja tanto si falla el username como si falla el password, mitigando ataques de enumeración de usuarios.

## Bloque 5. Criterios de aceptación
- **AC-01:** Proporcionar las credenciales correctas devuelve un token JWT con la expiración correspondiente.
- **AC-02:** Proporcionar un username que no existe devuelve un `InvalidCredentials` explícito (HTTP 401).
- **AC-03:** Proporcionar una contraseña errónea para un username válido devuelve `InvalidCredentials` explícito (HTTP 401).
