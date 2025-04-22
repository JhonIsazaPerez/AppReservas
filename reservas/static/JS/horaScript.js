// Obtener los botones de horarios y el botón de búsqueda
const timeButtons = document.querySelectorAll('.time-slots button');
const searchButton = document.querySelector('.search-reserve');
const timeselected = document.getElementById("selected-value");

// Variable para almacenar el horario seleccionado
let selectedTime = null;
function mostrarSeleccion(valor) {
  timeselected.textContent = "Tu hora seleccionada es: " + valor;
}
// Agregar eventos de clic a los botones de horarios
timeButtons.forEach(button => {
  button.addEventListener('click', () => {
    // Remover el estilo activo de todos los botones
    //timeButtons.forEach(btn => btn.classList.remove('active'));
    // Agregar el estilo activo al botón seleccionado
    //button.classList.add('active');
    selectedTime = button.textContent;
    mostrarSeleccion(selectedTime); //mostrar la hora seleccionada
    console.log(`Horario seleccionado: ${selectedTime}`);
  });
});

// Agregar evento de clic al botón de búsqueda
searchButton.addEventListener('click', () => {
  if (selectedTime != null) {
    fetch('/guardarDatos/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') // Token CSRF para seguridad en Django
      },
      body: JSON.stringify({ hora: selectedTime })
  })
  .then(response => response.json())
  .then(() => {
    window.location.href = "/infoUser/"; //abrir hora.html;
  })
  .catch(error => console.error("Error al guardar la fecha:", error));
    alert(`Has seleccionado el horario: ${selectedTime}`);
  } else {
    alert('Por favor, selecciona un horario para tu reserva.');
  }
});

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
  return cookieValue};

