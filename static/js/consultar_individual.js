document.addEventListener("DOMContentLoaded", function() {
    cargarGrupos();
    
    document.getElementById("grupo").addEventListener("change", cargarAsignaturas);
    });
    
        function cargarGrupos() {
            fetch("{{ url_for('obtener_grupos_por_carrera') }}")
            .then(response => response.json())
            .then(data => {
                let selectGrupo = document.getElementById("grupo");
                selectGrupo.innerHTML = '<option value="">--Seleccione--</option>';
                data.forEach(grupo => {
                    selectGrupo.innerHTML += `<option value="${grupo}">${grupo}</option>`;
                });
            })
            .catch(error => console.error("Error al cargar grupos:", error));
        }
    
        function cargarAsignaturas() {
    let grupo = document.getElementById("grupo").value;
    console.log("Grupo seleccionado:", grupo);
    
    if (!grupo) return;
    
    let formData = new FormData();
    formData.append("grupo", grupo);
    
    fetch("{{ url_for('obtener_asignaturas_por_carrera') }}", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Asignaturas recibidas:", data);
        let selectAsignatura = document.getElementById("asignatura");
        selectAsignatura.innerHTML = '<option value="">--Seleccione--</option>';
        data.forEach(asignatura => {
            selectAsignatura.innerHTML += `<option value="${asignatura}">${asignatura}</option>`;
        });
    })
    .catch(error => console.error("Error al cargar asignaturas:", error));
    }
    
    
        function consultarTutorias() {
            let asignatura = document.getElementById("asignatura").value;
            let grupo = document.getElementById("grupo").value;
    
            if (!asignatura || !grupo) {
                alert("Por favor, seleccione un grupo y una asignatura.");
                return;
            }
    
            let formData = new FormData();
            formData.append("asignatura", asignatura);
            formData.append("grupo", grupo);
    
            fetch("{{ url_for('buscar_tutoria') }}", {
                method: "POST",
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                let tabla = document.getElementById("tablaResultados");
                tabla.innerHTML = "";
    
                data.forEach(item => {
                    let fila = `<tr>
                        <td>${item.nombre}</td>
                        <td>${item.apellido_paterno}</td>
                        <td>${item.apellido_materno}</td>
                        <td>${item.matricula}</td>
                        <td>${item.cuatrimestre}</td>
                        <td>${item.motivo}</td>
                        <td>${item.fecha}</td>
                        <td>${item.descripcion}</td>
                        <td>${item.observacion}</td>
                        <td>${item.seguimiento}</td>
                    </tr>`;
                    tabla.innerHTML += fila;
                });
            })
            .catch(error => console.error("Error en la consulta:", error));
        }
    
        document.getElementById("grupo").addEventListener("change", cargarAsignaturas);