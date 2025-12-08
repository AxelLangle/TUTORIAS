// Función para obtener los grupos según la carrera seleccionada
function obtenerGrupos() {
    const carreraId = document.getElementById("carrera").value;
    if (carreraId) {
        fetch("/obtener_grupos_por_carrera", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ carrera_id: carreraId }),
        })
        .then(response => response.json())
        .then(grupos => {
            const grupoSelect = document.getElementById("grupo");
            grupoSelect.innerHTML = "<option value=''>Seleccione un grupo</option>"; // Limpiar grupos
            grupos.forEach(grupo => {
                const option = document.createElement("option");
                option.value = grupo.id_grupo;
                option.textContent = grupo.nombre;
                grupoSelect.appendChild(option);
            });
            obtenerAsignaturas(carreraId); // Obtener asignaturas correspondientes a la carrera
        });
    } else {
        document.getElementById("grupo").innerHTML = "<option value=''>Seleccione un grupo</option>";
    }
}

// Función para obtener los alumnos del grupo seleccionado
function obtenerAlumnos() {
    const grupoId = document.getElementById("grupo").value;
    if (grupoId) {
        fetch("/obtener_alumnos_por_grupo", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ grupo_id: grupoId }),
        })
        .then(response => response.json())
        .then(alumnos => {
            const alumnoSelect = document.getElementById("Nombre_alumno");
            alumnoSelect.innerHTML = "<option value=''>Seleccione el nombre de un alumno</option>"; // Limpiar alumnos
            alumnos.forEach(alumno => {
                const option = document.createElement("option");
                option.value = alumno.id_estudiante;
                option.textContent = `${alumno.nombre} ${alumno.apellido_paterno} ${alumno.apellido_materno}`;
                alumnoSelect.appendChild(option);
            });
        });
    } else {
        document.getElementById("Nombre_alumno").innerHTML = "<option value=''>Seleccione el nombre de un alumno</option>";
    }
}

// Función para obtener las asignaturas correspondientes a la carrera seleccionada
function obtenerAsignaturas(carreraId) {
    if (carreraId) {
        fetch("/obtener_asignaturas_por_carrera", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ carrera_id: carreraId }),
        })
        .then(response => response.json())
        .then(asignaturas => {
            const asignaturaSelect = document.getElementById("asignatura");
            asignaturaSelect.innerHTML = "<option value=''>Seleccione una asignatura</option>"; // Limpiar asignaturas
            asignaturas.forEach(asignatura => {
                const option = document.createElement("option");
                option.value = asignatura.id_asignatura;
                option.textContent = asignatura.nombre;
                asignaturaSelect.appendChild(option);
            });
        });
    }
}