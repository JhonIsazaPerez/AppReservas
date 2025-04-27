document.addEventListener('DOMContentLoaded', function() {
<<<<<<< HEAD
    // Elementos principales 
    const numeroButtons = document.querySelectorAll('.numero');
    const plusButton = document.getElementById('plus-button');
    const modal = document.getElementById('modal');
    const modalInput = document.getElementById('modal-input');
    const modalConfirm = document.getElementById('modal-confirm');
    const modalClose = document.getElementById('modal-close');
    const selectedValue = document.getElementById('selected-value');
    const hiddenInput = document.getElementById('number_of_people');
    const form = document.querySelector('form');
    
    // Manejo de selección de botones numéricos
    numeroButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Quitar selección previa
            numeroButtons.forEach(btn => btn.classList.remove('selected'));
            
            // Marcar como seleccionado
            this.classList.add('selected');
            
            // Actualizar el valor en el formulario
            hiddenInput.value = this.value; // Usar el valor del botón
            
            // Mostrar selección al usuario
            selectedValue.textContent = `Personas seleccionadas: ${this.textContent}`;
        });
    });
    
    // Modal para número personalizado
    plusButton.addEventListener('click', function() {
        modal.classList.remove('hidden');
    });
    
    modalClose.addEventListener('click', function() {
        modal.classList.add('hidden');
        modalInput.value = '';
    });
    
    modalConfirm.addEventListener('click', function() {
        const inputValue = modalInput.value;
        
        if (inputValue && !isNaN(inputValue) && parseInt(inputValue) > 0 && parseInt(inputValue) <= 15) {
            // Quitar selecciones previas
            numeroButtons.forEach(btn => btn.classList.remove('selected'));
            
            // Actualizar valor en formulario
            hiddenInput.value = inputValue;
            selectedValue.textContent = `Personas seleccionadas: ${inputValue}`;
            
            // Cerrar modal
            modal.classList.add('hidden');
        } else {
            alert('Por favor ingrese un número válido entre 1 y 15');
        }
    });
    
    // Validación antes de enviar - IMPORTANTE: asegurarse que se envía al endpoint correcto
    form.addEventListener('submit', function(e) {
        if (!hiddenInput.value) {
            e.preventDefault();
            alert('Por favor seleccione un número de personas');
            return false;
        }
        // Asegurarse que el formulario se envía a la URL correcta
        // NOTA: No modificar action si ya está configurado correctamente
        if (!form.action || form.action.includes('/guardarDatos/')) {
            form.action = window.location.pathname; // Usar la URL actual
        }
    });
  });
=======
  // Elementos principales 
  const numeroButtons = document.querySelectorAll('.numero');
  const plusButton = document.getElementById('plus-button');
  const modal = document.getElementById('modal');
  const modalInput = document.getElementById('modal-input');
  const modalConfirm = document.getElementById('modal-confirm');
  const modalClose = document.getElementById('modal-close');
  const selectedValue = document.getElementById('selected-value');
  const hiddenInput = document.getElementById('number_of_people');
  const form = document.querySelector('form');
  
  // Manejo de selección de botones numéricos
  numeroButtons.forEach(button => {
      button.addEventListener('click', function() {
          // Quitar selección previa
          numeroButtons.forEach(btn => btn.classList.remove('selected'));
          
          // Marcar como seleccionado
          this.classList.add('selected');
          
          // Actualizar el valor en el formulario
          hiddenInput.value = this.value; // Usar el valor del botón
          
          // Mostrar selección al usuario
          selectedValue.textContent = `Personas seleccionadas: ${this.textContent}`;
      });
  });
  
  // Modal para número personalizado
  plusButton.addEventListener('click', function() {
      modal.classList.remove('hidden');
  });
  
  modalClose.addEventListener('click', function() {
      modal.classList.add('hidden');
      modalInput.value = '';
  });
  
  modalConfirm.addEventListener('click', function() {
      const inputValue = modalInput.value;
      
      if (inputValue && !isNaN(inputValue) && parseInt(inputValue) > 0 && parseInt(inputValue) <= 15) {
          // Quitar selecciones previas
          numeroButtons.forEach(btn => btn.classList.remove('selected'));
          
          // Actualizar valor en formulario
          hiddenInput.value = inputValue;
          selectedValue.textContent = `Personas seleccionadas: ${inputValue}`;
          
          // Cerrar modal
          modal.classList.add('hidden');
      } else {
          alert('Por favor ingrese un número válido entre 1 y 15');
      }
  });
  
  // Validación antes de enviar - IMPORTANTE: asegurarse que se envía al endpoint correcto
  form.addEventListener('submit', function(e) {
      if (!hiddenInput.value) {
          e.preventDefault();
          alert('Por favor seleccione un número de personas');
          return false;
      }
      // Asegurarse que el formulario se envía a la URL correcta
      // NOTA: No modificar action si ya está configurado correctamente
      if (!form.action || form.action.includes('/guardarDatos/')) {
          form.action = window.location.pathname; // Usar la URL actual
      }
  });
});
>>>>>>> 97394bdbee1a9cc9910d1a036baf689a1577a20f
