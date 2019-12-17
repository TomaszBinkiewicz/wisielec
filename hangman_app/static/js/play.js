$(document).ready(function(){
    let buttons = $(".letter-buttons").find('button');
    let used_letters_div = $(".used_letters_div");
    let used_letters = used_letters_div.find('span');
    let used_list = [];
    for (let element of used_letters){
        used_list.push(element.innerText);
    }
    console.log(used_list);
    for (let button of buttons){
        if(used_list.includes(button.value)){
            button.classList.add("used_letter");
        }
    }
});