#importar los módulos necesarios
import tempfile
import os
import zipfile
from flask import Flask, request, redirect, send_file
from skimage import io
import base64
import glob
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import random  

# Inicializa la aplicación Flask
app = Flask(__name__)

# Directorio donde se guardan las imágenes
BASE_DIR = "static/images"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Variable global para almacenar la última imagen subida
last_uploaded_image = None

# Página HTML con la funcionalidad solicitada
main_html = """
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Generador de Símbolos Matemáticos</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <link
      rel="stylesheet"
      href="https://use.fontawesome.com/releases/v5.15.2/css/all.css"
      integrity="sha384-vSIIfh2YWi9wW0r9iZe7RJPrKwp6bG+s9QZMoITbCckVJqGCCRhc+ccxNcdpHuYu"
      crossorigin="anonymous"
    />
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');

      :root {
        --blue: #38B6FF;
        --chip-image: url("https://lh5.googleusercontent.com/y58mIMZC-IwE41TNehTaXikfD26LtOLULH3BRTAnFxSB33UHwDwf5wVfVvwVwsju1uo=w2400");
        --whiteish-letters: #dafffd;

      }

      * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
        font-size: 12px;
        font-family: 'IBM Plex Mono', sans-serif;
        color: white;
        font-size: 14px;
      }

      body {
        background-color: black;
        width: 100vw;
        height: 100vh;
      }

      main {
        padding: 50px;
        width: 100%;
        height: 100%;
        display: flex;
      /*   flex-direction: column; */
        flex-direction: row;
        align-items: center;
      }
      .menu {
        width: 220px;
      }
      .menu>button {
        width: 120px;
        height: 40px;
        padding-bottom: 5px;
        margin-top: 20px;
        background-color: transparent;
        background-image:url(https://lh6.googleusercontent.com/B3GZqaB4CtIuOZqveBVoBvWZPBZQ7bkkyTEXs9kBCWaop3KXDi5GaHa_zi9Dekl_igc=w2400);
        background-size: contain;
        background-repeat:no-repeat;
        transition: width 0.3s;
        border: none;
      }
      .menu>.btn:hover {
        color:var(--blue);
        background-color: transparent;
        box-shadow: none;
        width: 140px;
      }

      .scene {
        padding-left: 300px;
        width: 600px;
        height: 600px;
        perspective: 1800px;
      }

      a {
        text-decoration: none;
      }

      .cube {
        width: 100%;
        height: 100%;
        position: relative;
        transform-style:preserve-3d;
        transform: translateZ(-300px);
        transition: transform 1s;
      }

      .cube.show-front {
        transform: translateZ(-300px) rotateY(0deg);
      }
      .cube.show-right {
        transform: translateZ(-300px) rotateY(-90deg);
      }
      .cube.show-back {
        transform: translateZ(-300px) rotateY(-180deg);
      }
      .cube.show-left {
        transform: translateZ(-300px) rotateY(90deg);
      }
      .cube.show-top {
        transform: translateZ(-300px) rotateX(-90deg);
      }
      .cube.show-bottom {
        transform: translateZ(-300px) rotateX(90deg);
      }

      .df.fd-c {
        display: flex;
        flex-direction: column;
      }
      .df.fd-r {
        display: flex;
        flex-direction: row;
      }

      .cube-face {
        position: absolute;
        width: 600px;
        height: 600px;
        padding: 40px;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        background-color: rgba(0,0,0,0.8);
        background-image:var(--chip-image);
        background-size: contain;
        background-repeat: no-repeat;
      }

      .cube-face-front {
        transform: rotateY(0deg) translateZ(300px);

      }

      .intro-wrapper {
      /*   display: flex; */
        margin-bottom: 20px;
        align-items: center;
      }

      .image {
        border-radius: 50%;
        overflow: hidden;
        width: 150px;
        height: 150px;
        border: 1px dashed var(--blue);
      /*   display: flex; */
        justify-content: center;
        align-items: center;
        position: relative;
      }
.image-wrapper {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        overflow: hidden;
      }

      img {
        width: 100%;
        height: 140px;
        object-fit:cover;
      }

      .intro {
        width: 70%;
        margin-left: 20px;
      }

      .intro-heading {
        font-size: 3rem;
        font-family: 'IBM Plex Mono', monospace;
        width: 100%;
        color: var(--whiteish-letters);
        padding-bottom: 20px;
        line-height: 3rem;
      }

      .intro-heading>span {
        font-size: inherit;
        font-family: inherit;
        color: var(--blue);
      }

      .intro-text {
        color: var(--whiteish-letters);
        width: 90%;
        padding: 5px 0;
      }

      .buttons>button {
        color: var(--whiteish-letters);
        border: 2px solid var(--blue);
        background-color: transparent;
        padding: 5px 5px;
        margin: 5px;
        box-shadow: 0 0 10px var(--blue);
        transition: box-shadow 0.3s;
      }

      button:hover {
        cursor: pointer;
        box-shadow: 0 0 15px var(--blue);
        background-color: var(--blue);
      }

      .cube-face-back {
        transform: rotateY(180deg) translateZ(300px);
      }

      .cube-face-right {
        transform: rotateY(90deg) translateZ(300px);
      }

      .cube-face-left {
        transform: rotateY(-90deg) translateZ(300px);
      }

      .cube-face-top {
        transform: rotateX(90deg) translateZ(300px);
      }
      .cube-face-bottom {
        transform: rotateX(-90deg) translateZ(300px);
      }
      .social-media-btns {
        margin-top: 10px;
        margin-bottom: 40px;
      }
      .social-media-btns>a>i {
        font-size: 3rem;
        margin: 5px 10px;
      }
      .social-media-btns>a>i:hover {
        cursor: pointer;
        color: var(--blue);
      }
#myCanvas {
      border: 2px solid black;
      background-color: #38B6FF;
      margin-top: 20px;
}
.canvas-container {
      margin-top: 20px;
}

.btn-custom {
      margin-top: 10px;
}

.mensaje {
      font-size: 25px;
      margin-top: 7px;
      font-weight: bold;
      color: #a7d1ff;
}
    </style>
  </head>
  <body>
    <main>
      <div class="menu df fd-c">
        <button class="btn" data-side="front">Proyecto</button>
        <button class="btn" data-side="right">IntegranteI</button>
        <button class="btn" data-side="back">IntegranteII</button>
        <button class="btn" data-side="left">Informacion</button>
        <button class="btn" data-side="top">Enlace</button>
        <button class="btn" data-side="bottom">Creditos</button>
      </div>
      <section class="scene" >
        <div class="cube show-front" id="cube" data-side="front">
          <div class="cube-face cube-face-front">
            <div onload="InitThis();">
                <div class="container">
                  <div class="row">
                    <div class="col-md-6 offset-md-3 text-center">
                      <h1 class="mensaje" id="mensaje">Dibujando...</h1>
                      <canvas id="myCanvas" width="200" height="200"></canvas>
                      <div class="canvas-container">
                        <button onclick="clearArea();" class="btn btn-primary btn-custom">Borrar</button>
                        <form method="post" action="upload" onsubmit="prepareImg();" enctype="multipart/form-data">
                          <input id="numero" name="numero" type="hidden" value="">
                          <input id="myImage" name="myImage" type="hidden" value="">
                          <input id="bt_upload" type="submit" value="Enviar" class="btn btn-success btn-custom">
                        </form>
                        <label for="symbolSelect">Selecciona un símbolo:</label>
                        <select id="symbolSelect" onchange="updateSymbol();" class="form-control">
                          <option value="Σ">Σ (Sumatoria)</option>
                          <option value="E">E (Esperanza)</option>
                          <option value="O">O (Conjunto vacío)</option>
                          <option value="θ">θ (Ángulo)</option>
                        </select>
                        <br>
                        <a href="/download_last" class="btn btn-warning btn-custom">Descargar Última Imagen</a>
                        <a href="/download_all" class="btn btn-info btn-custom">Descargar Todas las Imágenes</a>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
          </div>

          <div class="cube-face cube-face-back">
            <div class="intro-wrapper df fd-r">
                <div class="intro">
                  <h1 class="intro-heading">
                    Hola, me llamo <span>Enrique</span> Orozco
                  </h1>
                  
                  <p class="intro-text">
                    Lorem ipsum dolor sit, amet consectetur adipisicing elit. Corporis unde temporibus maiores quis 
                    ab sunt voluptas sed delectus dolor dicta nam, ullam numquam reprehenderit. Quidem illum dignissimos
                     blanditiis totam nisi.
                  </p>
                </div>
                <div class="image df fd-r">
                  <div class="image-wrapper">
                    <img
                      src="https://th.bing.com/th/id/R.6470d7d30b5997ce362c7664314f4432?rik=3VMCpNN18rG0Ew&riu=http%3a%2f%2fgetdrawings.com%2fimg%2funknown-person-silhouette-3.png&ehk=IsDBIYW%2bZm8JmJ1aMq1LE2IgA5E9hoHv5NnBvRvPrTU%3d&risl=&pid=ImgRaw&r=0"
                      alt=""
                    />
                  </div>
                </div>
              </div>
          </div>

          <div class="cube-face cube-face-right">
            <div class="intro-wrapper df fd-r">
                <div class="intro">
                  <h1 class="intro-heading">
                    Hola, me llamo <span>Ruben</span> Cabrera
                  </h1>
                  
                  <p class="intro-text">
                    Lorem ipsum dolor sit, amet consectetur adipisicing elit. Corporis unde temporibus maiores quis 
                    ab sunt voluptas sed delectus dolor dicta nam, ullam numquam reprehenderit. Quidem illum dignissimos
                     blanditiis totam nisi.
                  </p>
                </div>
                <div class="image df fd-r">
                  <div class="image-wrapper">
                    <img
                      src="https://th.bing.com/th/id/R.6470d7d30b5997ce362c7664314f4432?rik=3VMCpNN18rG0Ew&riu=http%3a%2f%2fgetdrawings.com%2fimg%2funknown-person-silhouette-3.png&ehk=IsDBIYW%2bZm8JmJ1aMq1LE2IgA5E9hoHv5NnBvRvPrTU%3d&risl=&pid=ImgRaw&r=0"
                      alt=""
                    />
                  </div>
                </div>
              </div>
          </div>

          <div class="cube-face cube-face-left">
            <div class="intro-wrapper df fd-r">
                <div class="intro">
                  <h1 class="intro-heading">
                    Informacion sobre el  <span>Proyecto</span> 
                  </h1>
                  
                  <p class="intro-text">
                    Lorem ipsum dolor sit, amet consectetur adipisicing elit. Corporis unde temporibus maiores quis 
                    ab sunt voluptas sed delectus dolor dicta nam, ullam numquam reprehenderit. Quidem illum dignissimos
                     blanditiis totam nisi.
                  </p>
                </div>
                <div>
                  <div >
                    <img
                      src="https://aulavirtualmusica.com/inicio/images/cap.png"
                      alt=""
                    />
                  </div>
                </div>
              </div>
          </div>

          <div class="cube-face cube-face-top">
            <p class="intro-heading">Enlace a <span>los repositorios</span></p>
            <div class="social-media-btns">
                <h4 class="work-edu-heading">
                    <i class="fas fa-location-arrow"></i> Modelo de entrenamiento 
                  </h4>
              <a href="https://github.com/Rcabrera1221/Modelo-entrenamiento/blob/main/modeloentrenaminto_vision.ipynb" target="_blank"><i class="fab fa-github"></i></a>
              <h4 class="work-edu-heading">
                <i class="fas fa-location-arrow"></i> Alojamiento del github
            </h4>
            <a href="https://github.com" target="_blank"><i class="fab fa-github"></i></a>
            </div>
          </div>

          <div class="cube-face cube-face-bottom">
            <p class="intro-heading">Cre<span>ditos a</span></p>
            <div class="social-media-btns">
                <h4 class="work-edu-heading">
                    <i class="fas fa-location-arrow"></i> Programacion en español   
                  </h4>
              <a href="https://www.youtube.com/@programacion-es" target="_blank"><i class="fab fa-youtube"></i></a>
              <a href="https://github.com/pedrovelasquez9/tutorial-canvas-youtube/tree/master" target="_blank"><i class="fab fa-github"></i></a>
              <h4 class="work-edu-heading">
                <i class="fas fa-location-arrow"></i> Frank Andrade
            </h4>
            <a href="https://www.youtube.com/@thepycoachES" target="_blank"><i class="fab fa-youtube"></i></a>
            </div>
      </section>
    </main>
    <script>
        //Guardar el elemento y el contexto
const mainCanvas = document.getElementById("myCanvas");
const context = mainCanvas.getContext("2d");

let initialX;
let initialY;
let correccionX = 0;
let correccionY = 0;

let posicion = mainCanvas.getBoundingClientRect();
correccionX = posicion.x;
correccionY = posicion.y;

const dibujar = (cursorX, cursorY) => {
  context.beginPath();
  context.moveTo(initialX, initialY);
  context.lineWidth = 10;
  context.strokeStyle = "#000";
  context.lineCap = "round";
  context.lineJoin = "round";
  context.lineTo(cursorX, cursorY);
  context.stroke();

  initialX = cursorX;
  initialY = cursorY;
};

const mouseDown = (evt) => {
  evt.preventDefault();
  if ( evt.changedTouches === undefined) {
    initialX = evt.offsetX;
    initialY = evt.offsetY;
  }else{
    //evita desfase al dibujar
    initialX = evt.changedTouches[0].pageX - correccionX;
    initialY = evt.changedTouches[0].pageY - correccionY;
  }
  dibujar(initialX, initialY);
  mainCanvas.addEventListener("mousemove", mouseMoving);
  mainCanvas.addEventListener('touchmove', mouseMoving);
};

const mouseMoving = (evt) => {
  evt.preventDefault();
  if ( evt.changedTouches === undefined) {
    dibujar(evt.offsetX, evt.offsetY);
  }else{
    dibujar( evt.changedTouches[0].pageX - correccionX  , evt.changedTouches[0].pageY - correccionY );
  }
};

const mouseUp = () => {
  mainCanvas.removeEventListener("mousemove", mouseMoving);
  mainCanvas.removeEventListener("touchmove", mouseMoving);
};

mainCanvas.addEventListener("mousedown", mouseDown);
mainCanvas.addEventListener("mouseup", mouseUp);

//pantallas tactiles
mainCanvas.addEventListener('touchstart', mouseDown);
mainCanvas.addEventListener('touchend', mouseUp);
         const cube = document.getElementById("cube");

const clickOnSide = (side) => {
  const activeSide = cube.dataset.side;
  cube.classList.replace(`show-${activeSide}`, `show-${side}`);
  cube.setAttribute("data-side", side);
};

document.querySelectorAll(".btn").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    const sideToTurn = e.target.dataset.side;
    clickOnSide(sideToTurn);
  });
});
function clearArea() {
    const canvas = document.getElementById('myCanvas');
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
}

    function prepareImg() {
       var canvas = document.getElementById('myCanvas');
       document.getElementById('myImage').value = canvas.toDataURL();
    }

    function updateSymbol() {
        var selectedSymbol = document.getElementById('symbolSelect').value;
        document.getElementById('mensaje').innerHTML = 'Dibujando operador ' + selectedSymbol;
        document.getElementById('numero').value = selectedSymbol;
    }
</script>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>
"""

# Función para realizar data augmentation con múltiples transformaciones
def augment_image(image, num_augmented=1250):
    augmented_images = []

    while len(augmented_images) < num_augmented:
        # Crear una copia de la imagen original para aplicar transformación
        aug_img = image.copy()

        # Rotación aleatoria entre -45 y 45 grados
        angle = random.uniform(-45, 45)
        aug_img = aug_img.rotate(angle)

        # Escalado aleatorio entre 0.7x y 1.3x
        scale = random.uniform(0.7, 1.3)
        width, height = aug_img.size
        aug_img = aug_img.resize((int(width * scale), int(height * scale)))

        # Modificar brillo aleatorio entre 0.4x y 1.6x
        brightness_enhancer = ImageEnhance.Brightness(aug_img)
        brightness = random.uniform(0.4, 1.6)
        aug_img = brightness_enhancer.enhance(brightness)

        # Modificar contraste aleatorio entre 0.5x y 1.5x
        contrast_enhancer = ImageEnhance.Contrast(aug_img)
        contrast = random.uniform(0.5, 1.5)
        aug_img = contrast_enhancer.enhance(contrast)

        # Modificar nitidez aleatorio entre 0.5x y 1.5x
        sharpness_enhancer = ImageEnhance.Sharpness(aug_img)
        sharpness = random.uniform(0.5, 1.5)
        aug_img = sharpness_enhancer.enhance(sharpness)

        augmented_images.append(aug_img)

    return augmented_images

@app.route("/")
def main():
    """Sirve la página principal con el lienzo para dibujar."""
    return main_html

@app.route('/upload', methods=['POST'])
def upload():
    """Recibe y guarda la imagen enviada desde el navegador."""
    global last_uploaded_image
    try:
        # Obtener la imagen en base64 desde el formulario
        img_data = request.form.get('myImage').replace("data:image/png;base64,", "")
        operador = request.form.get('numero')

        # Crear el directorio correspondiente al operador
        operador_dir = os.path.join(BASE_DIR, operador)
        os.makedirs(operador_dir, exist_ok=True)

        # Guardar la imagen original
        original_path = os.path.join(operador_dir, f"{operador}_original.png")
        with open(original_path, "wb") as fh:
            fh.write(base64.b64decode(img_data))
        last_uploaded_image = original_path

        print(f"Imagen original guardada en: {original_path}")

        # Generar 1250 imágenes aumentadas para cada símbolo
        image = Image.open(original_path)
        augmented_images = augment_image(image, num_augmented=1250)
        base_name = os.path.splitext(os.path.basename(original_path))[0]

        # Guardar cada imagen aumentada en el mismo directorio
        for i, aug_image in enumerate(augmented_images):
            new_filename = f"{base_name}_aug_{i}.png"
            save_path = os.path.join(operador_dir, new_filename)
            try:
                aug_image.save(save_path)
                print(f"Guardando imagen aumentada en: {save_path}")
            except Exception as e:
                print(f"Error al guardar la imagen aumentada: {e}")

        print("Imágenes aumentadas generadas")

    except Exception as err:
        print(f"Ocurrió un error: {err}")

    # Redirige a la página principal
    return redirect("/", code=302)

@app.route('/download_last', methods=['GET'])
def download_last():
    """Permite al usuario descargar la última imagen subida."""
    global last_uploaded_image
    if last_uploaded_image:
        return send_file(last_uploaded_image, as_attachment=True)
    else:
        return "No hay imagen disponible para descargar."

@app.route('/download_all', methods=['GET'])
def download_all():
    """Permite al usuario descargar todas las imágenes generadas como un archivo ZIP."""
    zip_filename = "imagenes_generadas.zip"
    zip_filepath = os.path.join(BASE_DIR, zip_filename)

    # Crear un archivo ZIP con todas las imágenes en el directorio, organizadas por operador
    with zipfile.ZipFile(zip_filepath, "w") as zipf:
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file != zip_filename:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), BASE_DIR))

    return send_file(zip_filepath, as_attachment=True)

if __name__ == "__main__":
    # Ejecuta la aplicación Flask
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 4000)))