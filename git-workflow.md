📦 README – Flujo de trabajo Git (Main → Dev → Main)

⚠️ Este documento está escrito para alguien que NO entiende cómo funciona Git.
Léelo como si fuera una guía paso a paso sin asumir conocimientos previos.

🧠 ¿Qué es Git? (Explicado Simple)

Git es un sistema que:

Guarda versiones de tu código

Permite trabajar en cambios sin romper el proyecto principal

Permite volver atrás si algo sale mal

Piensa en Git como:

📸 Una cámara que toma fotos de tu proyecto (commits)

🌳 Un sistema de ramas (branches) donde puedes experimentar

🌳 ¿Qué son las ramas?

En este proyecto usaremos dos ramas:

main → Rama estable (producción)

dev → Rama donde desarrollamos

Regla importante:

Nunca desarrollamos directamente en main.

🔁 Flujo de trabajo correcto
📌 Estado inicial

Repositorio remoto (GitHub por ejemplo):

main

Creamos una rama de desarrollo:

dev
🚀 FLUJO COMPLETO PASO A PASO
1️⃣ Primera vez que clonas el proyecto
git clone URL_DEL_REPOSITORIO
cd nombre-del-proyecto

Ver ramas disponibles:

git branch -a

Cambiar a rama dev:

git checkout dev

Si no existe localmente:

git checkout -b dev origin/dev
2️⃣ Trabajar en DEV

Siempre antes de empezar:

git checkout dev
git pull origin dev

Esto significa:

Cambia a la rama dev

Descarga la última versión desde el servidor

✏️ Hacer cambios en el código

Después de modificar archivos:

Ver qué cambió:

git status

Agregar cambios:

git add .

Guardar cambios (commit):

git commit -m "Descripción clara de lo que hiciste"

Subir cambios a la nube:

git push origin dev
3️⃣ Cuando el desarrollo está listo

Ahora queremos pasar lo de dev a main.

Paso A: Cambiar a main
git checkout main

Actualizar main:

git pull origin main
Paso B: Mezclar dev dentro de main
git merge dev

Si no hay errores → perfecto.

Si hay conflictos:
Git te dirá qué archivos tienen conflicto.
Debes abrirlos y decidir qué código dejar.

Después:

git add .
git commit -m "Resolver conflictos"
Paso C: Subir main actualizado
git push origin main

Ahora producción está actualizada.

4️⃣ Sincronizar dev después de actualizar main

Esto es MUY importante.

Volvemos a dev:

git checkout dev

Traemos los cambios de main:

git merge main

Subimos dev actualizado:

git push origin dev
🔄 Flujo resumido
Trabajas en dev
↓
git push origin dev
↓
git checkout main
git merge dev
git push origin main
↓
git checkout dev
git merge main
git push origin dev
⚠️ Reglas importantes

Nunca hagas cambios directos en main.

Siempre:

pull antes de trabajar

push después de terminar

merge solo cuando algo está estable

🧩 ¿Qué significa cada comando?
Comando	Qué hace
git clone	Copia el repositorio
git checkout	Cambia de rama
git branch	Muestra ramas
git pull	Descarga cambios
git add	Prepara archivos
git commit	Guarda cambios
git push	Sube cambios
git merge	Une ramas
🛡️ Flujo recomendado profesional (más seguro)

En vez de hacer merge manual, usar Pull Requests:

Subes cambios a dev

En GitHub haces Pull Request dev → main

Revisas cambios

Apruebas

Merge automático

🧠 Concepto Mental Correcto

main = Producción estable

dev = Laboratorio

Commit = Foto

Branch = Línea de tiempo paralela

Merge = Unir líneas de tiempo

🏁 Conclusión

El flujo correcto es:

Desarrollar en dev
Subir a dev
Fusionar en main
Actualizar dev

Siempre en ese orden.

Si quieres, puedo hacerte:

🧠 Versión visual con diagrama

🛡️ Versión con Git Flow profesional

🚀 Versión para equipos grandes

🤖 Versión optimizada para proyectos con IA

Solo dime qué nivel quieres.


🛡️ Versión con Git Flow Profesional

Esta es una versión profesional usada en equipos reales.
Permite trabajar con estabilidad, control de versiones y releases formales.

🌳 Estructura de ramas
main        → Producción (código estable)
develop     → Integración de desarrollo
feature/*   → Nuevas funcionalidades
release/*   → Preparación de versiones
hotfix/*    → Correcciones urgentes en producción
📌 Rol de cada rama
🔵 main

Solo contiene código listo para producción.

Cada commit aquí representa una versión oficial.

🟢 develop

Rama base de desarrollo.

Aquí se integran todas las features terminadas.

Nunca se desarrolla directamente en main.

🟡 feature/nombre-feature

Se crean desde develop.

Contienen una sola funcionalidad.

Se eliminan después de integrarse.

Ejemplo:

feature/login-system
feature/payment-gateway
🟣 release/x.y.z

Se crean desde develop cuando todo está listo.

Se usa para:

Testing final

Ajustes menores

Cambio de versión

Luego se fusiona en:

main

develop

🔴 hotfix/x.y.z

Se crean desde main.

Se usan solo para errores críticos en producción.

Se fusionan en:

main

develop

🔁 Flujo profesional paso a paso
1️⃣ Crear nueva feature
git checkout develop
git pull origin develop
git checkout -b feature/nombre-feature

Trabajas normalmente:

git add .
git commit -m "Implement login validation"
git push origin feature/nombre-feature
2️⃣ Integrar feature a develop
git checkout develop
git pull origin develop
git merge feature/nombre-feature
git push origin develop

Eliminar rama:

git branch -d feature/nombre-feature
git push origin --delete feature/nombre-feature
3️⃣ Crear release
git checkout develop
git checkout -b release/1.0.0

Ajustes finales:

git commit -m "Bump version to 1.0.0"
git push origin release/1.0.0
4️⃣ Publicar release
git checkout main
git merge release/1.0.0
git push origin main

Actualizar develop:

git checkout develop
git merge release/1.0.0
git push origin develop

Eliminar rama release:

git branch -d release/1.0.0
5️⃣ Hotfix urgente
git checkout main
git checkout -b hotfix/1.0.1

Arreglas el bug:

git commit -m "Fix critical payment bug"
git push origin hotfix/1.0.1

Fusionar:

git checkout main
git merge hotfix/1.0.1
git push origin main

git checkout develop
git merge hotfix/1.0.1
git push origin develop
🎯 Ventajas del Git Flow

Separación clara de responsabilidades

Versionado profesional

Control de releases

Ideal para equipos grandes

🤖 Versión optimizada para proyectos con IA

Pensada para proyectos donde:

Hay prompts

Modelos LLM

Versionado de datasets

Experimentación constante

Cambios frecuentes

En proyectos con IA, el código NO es lo único importante.

También importan:

Prompts

Embeddings

Datasets

Configuraciones de modelo

Pipelines

🌳 Estructura recomendada de ramas para IA
main
develop
feature/*
experiment/*
model/*
dataset/*
prompt/*
🔵 main

Código estable

Modelo validado

Prompt aprobado

Dataset congelado

Solo versiones listas para producción

🟢 develop

Integración general

Cambios aprobados

Experimentos ya validados

🟡 feature/*

Cambios normales de backend o frontend.

🧪 experiment/*

Para pruebas de:

Nuevos prompts

Nuevas arquitecturas

Ajustes de temperatura

Cambios en chunking

Nuevas estrategias RAG

Ejemplo:

experiment/rag-chunking-v2
experiment/prompt-structured-output

Si funciona → merge a develop
Si no → se elimina

🧠 model/*

Cambios específicos de modelo:

model/gpt4-turbo-migration
model/claude-sonnet-test
model/local-llama3
📚 dataset/*

Cambios en datos:

dataset/cleaning-v2
dataset/embedding-update
📝 prompt/*

Versionado exclusivo de prompts:

prompt/system-v3
prompt/reasoning-chain-v2

Permite:

Comparar versiones

Hacer rollback de prompts

Evaluar impacto

🔁 Flujo recomendado en proyectos IA

Crear rama experiment/*

Probar cambios

Medir métricas (accuracy, latency, cost)

Si mejora → merge a develop

Cuando todo esté validado → merge a main

Taggear versión

🏷️ Versionado recomendado
v1.0.0-modelA-prompt3
v1.1.0-rag2
v2.0.0-architecture-change
📂 Extra recomendado para IA

Versionar también:

/prompts

/evaluations

/benchmarks

/metrics

/experiments

Y usar:

DVC (datasets grandes)

MLflow (tracking)

Weights & Biases (ML pesado)

🧠 Mentalidad correcta en proyectos con IA

En software tradicional:

Código es el producto.

En IA:

Prompt + Modelo + Datos + Evaluación = Producto

Si no versionas eso → no puedes reproducir resultados.

🏁 Conclusión
Git Flow profesional

Ideal para equipos grandes y productos tradicionales.

Git Flow optimizado para IA

Agrega ramas específicas para:

Experimentos

Modelos

Prompts

Datasets

Porque en IA, experimentar es parte del desarrollo formal.

Si quieres, puedo darte ahora:

🔥 Estructura de carpetas completa para IA profesional

🧬 Flujo ultra avanzado tipo laboratorio de investigación

🏢 Flujo enterprise con CI/CD para modelos

🚀 Plantilla base lista para usar

Dime qué nivel quieres construir.