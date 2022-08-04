let nameForm = document.getElementById("nameForm")
let nameDisplay = document.getElementById("nameDisplay")

let pronounForm = document.getElementById("pronounForm")
let pronounDisplay = document.getElementById("pronounDisplay")

let picForm = document.getElementById("picForm")
let picDisplay = document.getElementById("picDisplay")

let positionForm = document.getElementById("positionForm")
let positionDisplay = document.getElementById("positionDisplay")

let classForm = document.getElementById("classForm")
let classDisplay = document.getElementById("classDisplay")

let html = document.getElementsByTagName('html')[0]

let formElements = {
    positionDisplay : {
        "display": "inline-block",
        "form": {"element":positionForm,
                 "displayElement":positionDisplay},
    },
    picDisplay : {
        "display": "inline-block",
        "form": {"element":picForm,
                 "displayElement":picDisplay},
    },
    nameDisplay : {
        "display": "flex",
        "form": {"element":nameForm,
                 "displayElement":nameDisplay},
    },
    pronounDisplay : {
        "display": "inline-block",
        "form": {"element":pronounForm,
                 "displayElement":pronounDisplay},
    },
    classDisplay : {
        "display": "inline-block",
        "form": {"element":classForm,
                 "displayElement":classDisplay},
    }

}

tagNames = ["INPUT", "SELECT"]

html.addEventListener('click', e => {
    if ( e.target.className.includes("file-label") || e.target.tagName==="OPTION") {
        return
    }
    if (!tagNames.includes(e.target.tagName)) {
        for (let element in formElements) {
            if (formElements[element]["display"]) {
                formElements[element].hidden=false;
                formElements[element]["form"]["displayElement"].style.setProperty("display", formElements[element]["display"])
            }
            formElements[element]["form"]["element"].hidden = true 
        }        
    }
    if (e.target.className.includes("editable")) {
        e.target.hidden=true;
        e.target.style.setProperty("display", "none")
        let form = formElements[e.target.id]['form']['element']
        form.hidden = false;
        for (let i=0; i<form.length; i++){
            if (form[i].className.includes("select")||form[i].className.includes("input")) {
                form[i].focus()
                break
            }
        }
    }
})

