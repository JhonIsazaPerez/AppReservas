document.addEventListener("DOMContentLoaded", function() {
  const resultContainer = document.getElementById("selected-value");
  const plusButton = document.getElementById("plus-button");
  const modal = document.getElementById("modal");
  const modalInput = document.getElementById("modal-input");
  const modalConfirm = document.getElementById("modal-confirm");
  const modalClose = document.getElementById("modal-close");
  document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("modal");
    modal.classList.add("hidden"); // Asegúrate de que el modal esté oculto al cargar
  });
  document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("modal");
    
    console.log("Estado inicial del modal:", modal.classList.contains("hidden")); 
    // Esto debería imprimir 'true' si el modal está correctamente oculto al inicio.
  
    modal.classList.add("hidden"); // Fuerza que el modal esté oculto al cargar.
  });
  
  // Función para mostrar el modal
  function mostrarModal() {

    modal.classList.remove("hidden");
  }

  // Función para ocultar el modal
  function ocultarModal() {
    modal.classList.add("hidden");
    modalInput.value = ""; // Limpia el valor del input al cerrar
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
      ocultarModal(); // Cierra el modal después de confirmar
    }
  }

  // Evento para abrir el modal al hacer clic en '+'
  plusButton.addEventListener("click", mostrarModal);

  // Evento para el botón de confirmar
  modalConfirm.addEventListener("click", confirmarNumero);

  // Evento para cerrar el modal
  modalClose.addEventListener("click", function() {
    console.log("Botón 'Cerrar' presionado"); // Depuración en consola
    modal.classList.add("hidden"); // Oculta el modal
  });
});