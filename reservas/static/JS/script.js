document.addEventListener("DOMContentLoaded", function() {
  const buttoncontainer = document.getElementById("button-container");
  const resultContainer = document.getElementById("selected-value");
  const numericButtons = document.querySelectorAll(".numero");
  const plusButton = document.getElementById("plus-button");
  const modal = document.getElementById("modal");
  const modalInput = document.getElementById("modal-input");
  const modalConfirm = document.getElementById("modal-confirm");
  const modalClose = document.getElementById("modal-close");


  function mostrarSeleccion(valor) {
    resultContainer.textContent = "Seleccionaste: " + valor;
  }

  
  document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("modal");
    console.log("Estado inicial del modal:", modal.classList.contains("hidden")); 
    modal.classList.add("hidden");
  });

  function mostrarSeleccion(valor) {
    resultContainer.textContent = "Seleccionaste: " + valor;
  }

  // Evento para los botones numéricos
  numericButtons.forEach(function(button) {
    button.addEventListener("click", function() {
      const value = button.textContent;
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
});