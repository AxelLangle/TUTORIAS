
    // Detectar si el usuario intenta usar las flechas del navegador
    window.onpopstate = function(event) {
      // Mostrar la alerta al intentar navegar usando las flechas del navegador
      alert("Necesitas cerrar sesión desde el menú en la parte de perfil.");
      // Regresar al estado anterior (previene la navegación)
      history.go(1);
    };
  
    // Deshabilitar el uso de la tecla de retroceso (flecha atrás)
    window.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace') {
        alert("Necesitas cerrar sesión desde el menú en la parte de perfil.");
        e.preventDefault(); // Evitar que la tecla realice su acción
      }
    });
  
    // Prevenir la navegación hacia atrás usando la combinación de teclas Alt + Flecha izquierda
    window.addEventListener('popstate', function(e) {
      alert("Necesitas cerrar sesión desde el menú en el apartado de perfil.");
      history.pushState(null, null, location.href);
    });
  
    // Deshabilitar los botones de retroceso de la navegación
    history.pushState(null, null, location.href);
    window.addEventListener('popstate', function() {
      history.pushState(null, null, location.href);
    });