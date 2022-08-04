const title = document.getElementById("title")
const times = document.getElementsByClassName("time")
const form = document.getElementById('form')
const error = document.getElementById('errors')
const slides = document.getElementsByClassName('img-cb')
const hiddenText = document.getElementById("slideList")

var fixes = []
var borderColors = []
var selectedImgs = {}

// This adds a form validator to the front end of the code
// This way we don't really need it in the server side
// and we can display feedback to the user on how to update
// their information.

form.addEventListener('submit', (e) => {
    // This turns all of the border colors back to their original colors
    // This is incase the form was already submitted once with errors
    // and now has borders highlighted as red. If the fixed those errors
    // we don't want the red border to stay when they submit again.
    for (let i=0; i < fixes.length; i++) {
        fixes[i].style.borderColor = borderColors[i] 
    }

    // Reset the fixes back to empty and we will update with any errors
    // again. Fixes will hold all of the objects that need to be fixed.
    // BorderColors will be updated at the end with all of their original
    // border colors so we can turn them back from red after resubmission.
    fixes = []
    borderColors = []
    // Holds all the error messages to display
    let messages = []
    // State that tells us if there is at least one time error
    // So we don't add the message multiple times to messages
    // array.
    let timeError = false;

    // Checking that they have given the slideshow a title.
    if (title.value === '' || title.value == null) {
        messages.push("* Please enter a title for the slideshow.")
        fixes.push(title)
    }
    
    // This state trackes if at least one full day is filled in.
    let timeFilledState = false;

    // We want to loop through all of the possible times in 
    // groups of two. Start time and end time.
    for (let i=0; i<times.length; i=i+2) {
        // start time is time1
        let time1 = times[i]
        // end time is time2
        let time2 = times[i+1]
        // if ever both are filled then update the state.
        if (!timeFilledState && time1.value != '' && time2.value != '') {
            timeFilledState = true
        }
        // This is using XOR to check that both times have been
        // filled in and that one time is not just empty.
        if ((time1.value === '') != (time2.value === '')) {
            if (time1.value === '') {
                fixes.push(time1)
            } else {
                fixes.push(time2)
            }
            if (!timeError) {
                messages.push("* Times for each day must both be empty or both be filled.")
                timeError = true
            }     
        }

        // Checking if the start time is after the end time.
        if (time1.value > time2.value) {
            fixes.push(time1, time2)
            messages.push("* The start time must come before the end time.")
        }
    }

    // Checking that at least 1 full day has been filled in.
    if (!timeFilledState){
        messages.push("* Must have at least one day fully filled in.")
    }

    // Checking that at least 1 image has been selected.
    // Use CSS selectors to get everything that is selected.
    let imgs = document.querySelectorAll(".img-cb:checked")
    
    if (imgs.length == 0) {
        messages.push("* You must select at least one slide.")
    }

    // If there are any messages to be displayed don't submit
    // the form. Display the messages instead.
    if (messages.length > 0) {
        e.preventDefault()
        for (const element of fixes) {
            borderColors.push(element.style.borderColor)
            element.style.borderColor = 'red'
        }
        error.innerText = messages.join('\r\n')
    }

    // This bit of code gets all of the selected slides
    // and strips off the full path to just the file name
    // then adds it to a list. Then it sets the value of 
    // a hidden text input to the stringified version
    // of the list. This is is converted on the server 
    // side to an actual list.
    let imgsList = []
    for (let img of imgs){
        imgsList.push(img.value.split("_")[1])
    }
    console.log(imgsList)
    hiddenText.value = JSON.stringify(imgsList)
})

