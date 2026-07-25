# Insecure default configuration

# English

You are in the workspace directory `cybersecurity/001-insecure-config/`. It contains:
- `src/config.py` — the module to fix
- `tests/test_config.py` — tests that currently fail

The `load_config` function loads a JSON configuration string but applies insecure defaults: `debug=True`, `secret_key="changeme"`, and `allowed_hosts=["*"]`. It does not validate the values before returning them, so production deployments could end up with exposed debug information, a known hardcoded secret, and an unrestricted host allow-list.

Fix `src/config.py` so that:
- Hardcoded or default secrets such as `"changeme"` are rejected.
- Empty or very short secrets are rejected.
- In production mode, `debug` must be `False`.
- In production mode, `allowed_hosts` cannot be empty and cannot contain `"*"`.
- Secure defaults are applied when values are missing (`debug=False`, `allowed_hosts=["localhost"]`).

Your response must be the COMPLETE fixed content of `src/config.py`. Do not include explanations, markdown code fences, or any other text. Only the file content.

---

# Español

Estás en el directorio de trabajo `cybersecurity/001-insecure-config/`. Contiene:
- `src/config.py` — el módulo a corregir
- `tests/test_config.py` — las pruebas que actualmente fallan

La función `load_config` carga una cadena JSON de configuración pero aplica valores inseguros por defecto: `debug=True`, `secret_key="changeme"` y `allowed_hosts=["*"]`. No valida los valores antes de devolverlos, por lo que los despliegues de producción podrían terminar con información de depuración expuesta, un secreto conocido predefinido y una lista de hosts permitidos sin restricciones.

Corrige `src/config.py` para que:
- Se rechacen secretos predefinidos o codificados como `"changeme"`.
- Se rechacen secretos vacíos o muy cortos.
- En modo producción, `debug` sea `False`.
- En modo producción, `allowed_hosts` no esté vacío y no contenga `"*"`.
- Se apliquen valores seguros por defecto cuando faltan (`debug=False`, `allowed_hosts=["localhost"]`).

Tu respuesta debe ser el contenido completo corregido de `src/config.py`. No incluyas explicaciones, bloques de código markdown ni ningún otro texto. Solo el contenido del archivo.
