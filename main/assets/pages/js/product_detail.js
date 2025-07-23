
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
