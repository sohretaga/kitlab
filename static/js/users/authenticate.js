const signInBtn = document.querySelector("#sign-in-btn");
const signUpBtn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");
const url = new URL(window.location.href);
const params = new URLSearchParams(url.search);

const setUrlParams = (name, value) => {
  params.set(name, value);
  url.search = decodeURIComponent(params.toString());
  window.history.replaceState({}, '', url);
};

signUpBtn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
  setUrlParams('mode', 'sign-up');
});

signInBtn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
  setUrlParams('mode', 'sign-in');
});

const setPageMode = () => {
  const modeValue = params.get('mode');
  if (modeValue == 'sign-up'){
    signUpBtn.click();
  }
};

const checkPasswordOrUsername = () => {
  const usernameInput = document.getElementById('login-username').value;
  
  if (usernameInput) {
    notyf.error('İstifadəçi adı vəya şifrə yanlışdır!');
  }
};

const checkRegisterHaveError = () => {
  const error = document.getElementById('error').value;
  if (error) {
    if (error == 'username') {
      notyf.error('Bu istifadəçi adı artıq istifadə olunur.');
    } else if (error == 'email') {
      notyf.error('Bu e-poçt artıq istifadə olunur.');
    }
  }
};

const checkParamFromBackend = () => {
  const mode = document.getElementById('mode').value;
  if (mode) {
    setUrlParams('mode', mode);
  }
};

checkPasswordOrUsername();
checkRegisterHaveError();
checkParamFromBackend();
setPageMode();

function checkFormValid(button, mode) {
  if (mode == 'login') {

    const usernameInput = document.getElementById('login-username').value;
    const passwordInput = document.getElementById('login-password').value;

    if (!usernameInput || !passwordInput) {
      notyf.error('İstifadəçi adı və şifrə yazılmalıdır!');
      return;
    }

  } else if (mode == 'register') {

    const fullName = document.getElementById('full-name').value;
    const usernameInput = document.getElementById('register-username').value;
    const email = document.getElementById('email').value;
    const passwordInput1 = document.getElementById('register-password1').value;
    const passwordInput2 = document.getElementById('register-password2').value;

    if (!fullName) {
      notyf.error('Ad Soyad yazılmalıdır!');
      return;
    }

    if (!usernameInput) {
      notyf.error('İstifadəçi adı yazılmalıdır!');
      return;
    }

    if (!email) {
      notyf.error('Email yazılmalıdır!');
      return;
    }

    if (!passwordInput1 || !passwordInput2) {
      notyf.error('Şifrə yazılmalıdır!');
      return;
    }else {
      if (passwordInput1 != passwordInput2) {
        notyf.error('Şifrələr eyni olmalıdır!');
        return;
      }else {
        if (passwordInput1.length < 6) {
          notyf.error('Şifrə ən az 6 simvol olmalıdır!');
          return;
        }
      }
    }

    const mode = document.getElementById('mode');
    mode.value = 'sign-up';
  }

  const form = button.closest('form');
  form.submit();
};

document.addEventListener('keydown', (event) => {
  
  if (event.key == 'Enter') {
    if (container.classList.contains('sign-up-mode')) {
      document.getElementById('register-btn').click();
    }else {
      document.getElementById('login-btn').click();
    }
  }
});