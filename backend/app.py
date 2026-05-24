from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/getCatsInfo')
def getCatsInfo():
    content = """# Felis catus
El gato doméstico (Felis catus, también Felis silvestris catus), llamado comúnmente gato, y de forma coloquial minino, michino o michi, y algunos nombres más, es un mamífero carnívoro de la familia Felidae (también conocida como "felina").

Junto con el perro, el gato es el animal doméstico más popular como mascota. En 2017, la población mundial estimada de gatos estaba en seiscientos millones de felinos. En esta cifra se incluyeron gatos que son mascota, gatos callejeros (sin hogar) y gatos salvajes; sumando solo los gatos silvestres alrededor de 100 millones. El país considerado hasta esa fecha que más felinos tiene como mascota es Estados Unidos. Rusia contaba con aproximadamente 23 millones de gatos domésticos en 2021 convirtiéndose en el país europeo con mayor población de este tipo de felinos.

Por su amplio abanico de presas potenciales, por su alta eficiencia como depredador y por su elevado éxito reproductivo —especialmente si se suministra artificialmente alimento a las colonias sin tomar medidas adicionales para limitar su fertilidad— el gato doméstico está incluido en la lista de las cien especies exóticas invasoras más dañinas del mundo de la Unión Internacional para la Conservación de la Naturaleza.

Fuente: https://es.wikipedia.org/wiki/Felis_catus"""

    value = {
        "title": "Felis catus",
        "content": content
    }

    return jsonify(value)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)