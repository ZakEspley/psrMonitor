const form = document.getElementById('form');
const error = document.getElementById('errors');
const fileInput2 = document.getElementById('file');

// var fixes = []
// var borderColors = []
// var selectedImgs = {}

// This adds a form validator to the front end of the code
// This way we don't really need it in the server side
// and we can display feedback to the user on how to update
// their information.

// papaSyncRead = async (file) => {
//     let result = await new Promise((resolve) => {
//         Papa.parse(file, {
//             header:true,
//             complete: (result) => resolve()
//         })
//     })
// }

async function parseCsv(file) {
    return await new Promise((resolve, reject) => {
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        transform: (value) => {
          return value.trim();
        },
        complete: (results) => {
          return resolve(results);
        },
        error: (error) => {
          return reject(error);
        },
      });
    });
  }

completed = (results, file, messages) => {
  handleErrors(messages, results.data)
  error.innerText = messages.join('\r\n')
    // If there are any messages to be displayed don't submit
    // the form. Display the messages instead.
  if (messages.length === 0) {
      form.submit() 
  }
}

errored = (results, file) => {
  console.log(results)
}

function handleErrors(messages, csv) {
  if (csv.length === 0) {
    messages.push("* You're CSV file is empty.")
  }

  if (Object.keys(csv[0]).length < 4) {
    messages.push("* There are too few columns in your CSV")
  }

  for (const key of ["Day", "Start Time", "End Time", "Assistant 1"]) {
    if (!(key in csv[0])) {
      messages.push("* Your CSV file does not have the heading: " + key)
    }
  }
  let missingData = false
  // for (const host of csv) {
  //   for (const key in host) {
  //     console.log("Logging")
  //     console.log(host, key)
  //     console.log(host[key])
  //     if (host[key] == null || host[key] ==="") {
  //       messages.push("* Missing Data in CSV")
  //       missingData=true
  //       break
  //     }
  //   }
  //   if (missingData) {
  //     break
  //   }
  // }


}


form.addEventListener('submit', async (e) => {
    e.preventDefault()
    let file = fileInput2.files[0]
    // // This turns all of the border colors back to their original colors
    // // This is incase the form was already submitted once with errors
    // // and now has borders highlighted as red. If the fixed those errors
    // // we don't want the red border to stay when they submit again.
    // for (let i=0; i < fixes.length; i++) {
    //     fixes[i].style.borderColor = borderColors[i] 
    // }

    // // Reset the fixes back to empty and we will update with any errors
    // // again. Fixes will hold all of the objects that need to be fixed.
    // // BorderColors will be updated at the end with all of their original
    // // border colors so we can turn them back from red after resubmission.
    // fixes = []
    // borderColors = []
    // Holds all the error messages to display
    let messages = []
    Papa.parse(file, {
      header:true,
      complete:(results, files) => completed(results, file, messages),
      error: errored
    })
})

