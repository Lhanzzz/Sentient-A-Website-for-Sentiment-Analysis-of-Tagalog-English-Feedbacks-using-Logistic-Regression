function changeRegisters(){
    var login = document.getElementById("login");
    var register = document.getElementById("register");
    var change = document.getElementById("change");
    

    if(change.innerHTML=="Create an Account"){
       
        change.innerHTML = "Login your account";
        register.style.display = "flex";
        login.style.display = "none";
    }

    else{

        change.innerHTML = "Create an Account";
        login.style.display = "flex";
        register.style.display = "none";

    }
}




function addmore(){
    var item = document.getElementById("itemeqweqw");
    var file = document.getElementById("file");
    var form = document.getElementById("FilterForm");
    var submit = document.getElementById("submit");
    var add = document.getElementById("buttonaddmore").value;
   
    var number =parseInt(add);
 
    if (number%2 == 1) {
        number+=1;
        document.getElementById("buttonaddmore").value = number;
        form.style.display = "block";
        submit.style.display = "block";
        item.style.display = "block";
        file.style.display = "block";
     
    }
    else{
        document.getElementById("buttonaddmore").value = number - 1;
        form.style.display = "none";
        submit.style.display = "none";
        item.style.display = "none";
        file.style.display = "none";
        
     


    }

 
  

}