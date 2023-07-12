function changeBg(){
    var navbar = document.getElementById("navigator");
    var navbarlogin = document.getElementById("login");
    var scrollbar = window.scrollY;

    if(scrollbar > 1000){
        navbar.classList.add("navchangecolor");
        navbarlogin.classList.add("navlogincolor");
    }
    else{
        navbar.classList.remove("navchangecolor");
        navbarlogin.classList.remove("navlogincolor");
    }
}

window.addEventListener('scroll',changeBg);

