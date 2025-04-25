document.addEventListener("DOMContentLoaded", function() {
  const dateInput = document.getElementById("reservation-date"); 
  const form = document.querySelector("form"); // Formulario principal
  const timeButton = document.getElementById("search-time"); // Botón para verificar horarios disponibles
  // Variables para la fecha mínima y máxima
  const today = new Date();
  const maxDate = new Date();
  maxDate.setDate(today.getDate() + 15); // Fecha máxima: dentro de 15 días

  // Función para formatear fechas en formato "YYYY-MM-DD"
  const formatDate = (date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
  };

  // Asignar fechas mínima y máxima al campo de entrada
  if (dateInput) {
      dateInput.min = formatDate(today); // Fecha mínima: Hoy
      dateInput.max = formatDate(maxDate); // Fecha máxima: Dentro de 30 días
  }
  timeButton.addEventListener("submit", function(e) {
    if (!dateInput.value) {
      e.preventDefault();
      alert('Por favor seleccione una fecha para su reserva');
      return false;
  }
  // Asegurarse que el formulario se envía a la URL correcta
  // NOTA: No modificar action si ya está configurado correctamente
  if (!form.action || form.action.includes('/guardarDatos/')) {
      form.action = window.location.pathname; // Usar la URL actual
    }
  });
});


/*
  // Evento al hacer clic en el botón "VER HORARIOS DISPONIBLES"
  timeButton.addEventListener("click", function() {
      const selectedDate = dateInput.value; // Obtener la fecha seleccionada por el usuario
      if (selectedDate) {
          fetch('/guardarDatos/', { // Ruta del backend (ajústala si es necesario)
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': getCookie('csrftoken') // Token CSRF para seguridad
              },
              body: JSON.stringify({ date: selectedDate }) // Enviar la fecha como JSON
          })
          .then(response => {
              if (!response.ok) throw new Error("Error al guardar la fecha");
              return response.json();
          })
          .then(() => {
              window.location.href = "/hora/"; // Redirigir al siguiente paso
          })
          .catch(error => {
              console.error("Error al guardar la fecha:", error);
              alert("Ocurrió un error al procesar tu solicitud.");
          });
      } else {
          alert("Por favor selecciona una fecha para continuar.");
      }
  });
});

// Función para obtener el token CSRF de las cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
  */   