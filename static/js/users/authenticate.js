const signInBtn = document.querySelector("#sign-in-btn");
const signUpBtn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

signUpBtn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

signInBtn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});

const checkPasswordOrUsername = () => {
  const usernameInput = document.getElementById('username').value;
  
  if (usernameInput) {
    notyf.error('İstifadəçi adı vəya şifrə yanlışdır!');
  }
}

checkPasswordOrUsername();

function checkFormValid(button) {
  const usernameInput = document.getElementById('username').value;
  const passwordInput = document.getElementById('password').value;

  if (!usernameInput || !passwordInput) {
    notyf.error('İstifadəçi adı və şifrə yazılmalıdır!');
    return;
  }

  const form = button.closest('form');
  form.submit();
};