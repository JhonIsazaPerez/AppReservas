// Obtener los botones de horarios, el botón de búsqueda y el campo oculto
const timeButtons = document.querySelectorAll('.time-slots button');
const searchButton = document.querySelector('.search-reserve');
const hiddenTimeInput = document.getElementById('selected-time');
const timeselected = document.getElementById("selected-value");

// Variable para almacenar el horario seleccionado
let selectedTime = null;

// Agregar eventos de clic a los botones de horarios
timeButtons.forEach(button => {
  button.addEventListener('click', function () {
    // Actualizar el horario seleccionado
    selectedTime = this.getAttribute('data-value');
    hiddenTimeInput.value = selectedTime; // Actualizar el valor del campo oculto
    timeselected.textContent = `Tu hora seleccionada es: ${this.textContent}`;
    
    console.log(`Horario seleccionado: ${selectedTime}`);
  });
});

// Agregar evento al formulario para evitar el envío si no se selecciona una hora
const form = document.getElementById('time-form');
form.addEventListener('submit', function (event) {
  if (!selectedTime) {
    event.preventDefault();
    alert('Por favor, seleccione una hora antes de continuar.');
  }
  if (!form.action || form.action.includes('/guardarDatos/')) {
    form.action = window.location.pathname;}
});

/*
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
    window.location.href = "/infoUser/"; //abrir infoUser.html;
  })
  .catch(error => console.error("Error al guardar la fecha:", error));
    
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
  return cookieValue};*/

