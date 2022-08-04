let nameForm = document.getElementById("nameForm")
let nameDisplay = document.getElementById("nameDisplay")
let nameEdit = document.getElementById("nameEdit")


nameEdit.addEventListener("click", e => {
    // Hides the profile name and reveals the form
    nameDisplay.hidden = true;
    nameDisplay.style.setProperty("display", "none")
    nameForm.hidden = false;
})

nameForm.addEventListener('submit', e => {
    nameDisplay.hidden = false
    nameDisplay.style.setProperty("display", "flex")
    nameForm.hidden = true;
})

let pronounForm = document.getElementById("pronounForm")
let pronounDisplay = document.getElementById("pronounDisplay")

pronounDisplay.addEventListener("click", e => {
    // Hides the profile pronoun and reveals the form
    pronounDisplay.hidden = true;
    pronounDisplay.style.setProperty("display", "none")
    pronounForm.hidden = false;
})

pronounForm.addEventListener('submit', e => {
    pronounDisplay.hidden = false
    pronounDisplay.style.setProperty("display", "flex")
    pronounForm.hidden = true;
})

let picForm = document.getElementById("picForm")
let picDisplay = document.getElementById("picDisplay")

picDisplay.addEventListener("click", e => {
    // Hides the profile pic and reveals the form
    // picDisplay.hidden = true;
    // picDisplay.style.setProperty("display", "none")
    picForm.hidden = false;
})

picForm.addEventListener('submit', e => {
    picForm.hidden = true;
})

