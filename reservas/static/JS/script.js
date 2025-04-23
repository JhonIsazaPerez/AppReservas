document.addEventListener("DOMContentLoaded", function() {
  const buttoncontainer = document.getElementById("button-container");
  const resultContainer = document.getElementById("selected-value");
  const numericButtons = document.querySelectorAll(".numero"); // Definir aquí
  const plusButton = document.getElementById("plus-button");
  const modal = document.getElementById("modal");
  const modalInput = document.getElementById("modal-input");
  const modalConfirm = document.getElementById("modal-confirm");
  const modalClose = document.getElementById("modal-close");
  const searchButton = document.getElementById("search-reservation")
  let numeroPersonas;//valor seleccionado por el usuario
  ;

  function mostrarSeleccion(valor) {
    resultContainer.textContent = "Número de personas: " + valor;
  }

  // Evento para los botones numéricos
  numericButtons.forEach(function(button) {
    button.addEventListener("click", function() {
      const value = button.textContent;
      numeroPersonas = value; // Guardar el valor seleccionado
      mostrarSeleccion(value);
    });
  });

  // Función para mostrar el modal
  function mostrarModal() {
    modal.classList.remove("hidden");
  }

  // Función para ocultar el modal
  function ocultarModal() {
    modal.classList.add("hidden");
    modalInput.value = "";
  }

  // Función para manejar la confirmación del número
  function confirmarNumero() {
    const value = parseInt(modalInput.value, 10);
    if (isNaN(value)) {
      alert("Por favor, ingresa un número válido.");
    } else if (value > 15) {
      alert("El número no puede ser mayor a 15.");
      modalInput.value = ""; // Limpiar el cuadro de texto
    } else {
      valor = value; // Guardar el valor seleccionado
      resultContainer.textContent = "Seleccionaste: " + value;
      ocultarModal();
    }
  }

  // Evento para abrir el modal al hacer clic en '+'
  plusButton.addEventListener("click", mostrarModal);

  // Evento para el botón de confirmar
  modalConfirm.addEventListener("click", confirmarNumero);

  // Evento para cerrar el modal
  modalClose.addEventListener("click", ocultarModal);

  // Muestra el calendario al hacer clic en "Buscar Reserva"
  searchButton.addEventListener("click", function() {
    if (numeroPersonas != null) {
      fetch('guardarDatos/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Token CSRF para seguridad en Django
        },
        body: JSON.stringify({ numero_personas: numeroPersonas })
    })
    .then(response => response.json())
    .then(() => {
        window.location.href = "/calendario/"; // Redirige a la página calendario
    })
    .catch(error => console.error("Error al guardar número de personas:", error));
}
    else{alert("Por favor, selecciona un número antes de continuar.");}
  });
  // Función para obtener el token CSRF
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

});
