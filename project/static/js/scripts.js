const menuToggle = document.querySelector('.mobile-menu-toggle');
const menu = document.querySelector('.menu');

// Função para alternar o menu no mobile
menuToggle.addEventListener('click', () => {
  menu.classList.toggle('active');
});

// Função para fechar o menu quando a tela for redimensionada para desktop
function checkScreenWidth() {
  if (window.innerWidth > 768) {
    // Fechar o menu se a tela for maior que 768px
    menu.classList.remove('active');
  }
}

// Chama a função na inicialização para garantir que o menu esteja fechado
checkScreenWidth();

// Adiciona o evento de resize
window.addEventListener('resize', checkScreenWidth);