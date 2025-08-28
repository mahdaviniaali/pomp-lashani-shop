
// Update selected variant when user changes selection
document.addEventListener('DOMContentLoaded', function() {
  const variantInputs = document.querySelectorAll('input[name="variant"]');
  const selectedVariantInput = document.getElementById('selected-variant');
  
  variantInputs.forEach(input => {
    input.addEventListener('change', function() {
      if(this.checked) {
        selectedVariantInput.value = this.value;
      }
    });
  });
});

// Mobile-specific functionality
document.addEventListener('DOMContentLoaded', function() {
  // Check if we're on mobile
  const isMobile = window.innerWidth <= 991;
  
  if (isMobile) {
    // Add smooth scrolling to prevent content jumping
    const fixedSection = document.querySelector('.fixed-section');
    if (fixedSection) {
      // Add padding to body to prevent content from being hidden
      document.body.style.paddingBottom = '80px';
    }
    
    // Improve touch interactions for quantity buttons
    const quantityButtons = document.querySelectorAll('.btn-quantity');
    quantityButtons.forEach(button => {
      button.addEventListener('touchstart', function(e) {
        this.style.transform = 'scale(0.95)';
      });
      
      button.addEventListener('touchend', function(e) {
        this.style.transform = 'scale(1)';
      });
    });
    
    // Add haptic feedback for mobile devices
    if ('vibrate' in navigator) {
      const actionButtons = document.querySelectorAll('.butn, .btn-quantity');
      actionButtons.forEach(button => {
        button.addEventListener('click', function() {
          navigator.vibrate(50);
        });
      });
    }
    
    // Prevent zoom on input focus for better mobile experience
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
      input.addEventListener('focus', function() {
        this.style.fontSize = '16px'; // Prevents zoom on iOS
      });
    });
  }
  
  // Handle variant selection changes for mobile
  const variantRadios = document.querySelectorAll('input[name="variant"]');
  variantRadios.forEach(radio => {
    radio.addEventListener('change', function() {
      if (this.checked) {
        // Trigger HTMX request to update the product list
        const productList = document.querySelector('#product-list');
        if (productList && productList.hasAttribute('hx-get')) {
          // Use HTMX API to trigger the request
          if (typeof htmx !== 'undefined') {
            htmx.trigger(productList, 'change');
          }
        }
      }
    });
  });
});

// Add loading states for better UX
document.addEventListener('htmx:beforeRequest', function(evt) {
  const target = evt.target;
  if (target.classList.contains('btn-quantity') || target.classList.contains('butn')) {
    target.style.opacity = '0.7';
    target.style.pointerEvents = 'none';
  }
});

document.addEventListener('htmx:afterRequest', function(evt) {
  const target = evt.target;
  if (target.classList.contains('btn-quantity') || target.classList.contains('butn')) {
    target.style.opacity = '1';
    target.style.pointerEvents = 'auto';
  }
});
