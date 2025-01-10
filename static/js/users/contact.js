const formSuccessStatus = document.querySelector("meta[name='form-success']").getAttribute('content');

if (formSuccessStatus) {
    notyf.open({
        type: 'info',
        message: 'Formunuz göndərilid!\nTezliklə sizinlə əlaqə saxlanılacaq.'
      });
}

function checkFormValid(button) {
    const fullNameInput = document.getElementById('full-name').value;
    const emailInput = document.getElementById('email').value;
    const messageInput = document.getElementById('message').value;
  
    if (!fullNameInput) {
      notyf.error('Ad Soyad yazılmalıdır!');
      return;
    }
  
    else if (!emailInput) {
      notyf.error('Email yazılmalıdır!');
      return;
    }
  
    else if (!messageInput) {
      notyf.error('Mesaj yazılmalıdır!');
      return;
    }
  
    const form = button.closest('form');
    form.submit();
  };