from flask import Flask, render_template, jsonify, request, redirect
import json
import os
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader

# Cloudinaryの初期設定（取得した情報をここに入れる）
cloudinary.config(
    cloud_name="dahgrxpky",
    api_key="664612899882299",
    api_secret="kwMpxye5K46cW0XQewXHXf0-m3I"
)


POINTS_JSON = "data/points.json"
IMAGE_FOLDER = "static/images/points/"
app = Flask(__name__)


@app.route("/add", methods=["GET", "POST"])
def add_point():
    if request.method == "POST":
        map_id = request.form["map"]
        side = request.form["side"]
        agent = request.form["agent"]
        title = request.form["title"]
        description = request.form["description"]

        # 画像3枚取得
        stand_file = request.files["stand_image"]
        point_file = request.files["point_image"]
        extra_file = request.files["extra_image"]

        # JSON読み込み
        if os.path.exists(POINTS_JSON):
            with open(POINTS_JSON, "r", encoding="utf-8") as f:
                try:
                    points = json.load(f)
                except json.JSONDecodeError:
                    points = []
        else:
            points = []

        # 次のID
        new_id = len(points) + 1

        # Cloudinaryにアップロード（ファイル名も付けておくと整理しやすい）
        stand_result = cloudinary.uploader.upload(stand_file, public_id=f"points/{new_id}_stand")
        point_result = cloudinary.uploader.upload(point_file, public_id=f"points/{new_id}_point")
        extra_result = cloudinary.uploader.upload(extra_file, public_id=f"points/{new_id}_extra")

        # URLを取得
        stand_url = stand_result["secure_url"]
        point_url = point_result["secure_url"]
        extra_url = extra_result["secure_url"]

        # 定点データを作成
        new_point = {
            "id": new_id,
            "map": map_id,
            "side": side,
            "agent": agent,
            "title": title,
            "description": description,
            "stand_image": stand_url,
            "point_image": point_url,
            "extra_image": extra_url
        }

        # 保存
        points.append(new_point)
        with open(POINTS_JSON, "w", encoding="utf-8") as f:
            json.dump(points, f, indent=2, ensure_ascii=False)

        return "登録完了！<br><a href='/add'>もう一度追加する</a>"

    return render_template("add.html")


@app.route("/delete/<int:point_id>", methods=["POST"])
def delete_point(point_id):
    # ファイルとJSON読み込み
    if os.path.exists(POINTS_JSON):
        with open(POINTS_JSON, "r", encoding="utf-8") as f:
            try:
                points = json.load(f)
            except json.JSONDecodeError:
                points = []
    else:
        points = []

    # 対象のポイントを除外
    updated_points = [p for p in points if p["id"] != point_id]

    # 対応する画像を削除（あれば）
    image_file = os.path.join(IMAGE_FOLDER, f"{point_id}.jpg")
    if os.path.exists(image_file):
        os.remove(image_file)

    # JSON更新
    with open(POINTS_JSON, "w", encoding="utf-8") as f:
        json.dump(updated_points, f, indent=2, ensure_ascii=False)

    return redirect(request.referrer or "/")



@app.route("/")
def index():
    with open("data/maps.json", encoding="utf-8") as f:
        maps = json.load(f)
    return render_template("index.html", maps=maps)

@app.route("/map/<map_id>")
def select_side(map_id):
    return render_template("map.html", map_id=map_id)

@app.route("/map/<map_id>/side/<side>")
def select_role(map_id, side):
    return render_template("role.html", map_id=map_id, side=side)


@app.route("/map/<map_id>/side/<side>/role/<role>")
def select_agent_by_role(map_id, side, role):
    with open("data/agents.json", "r", encoding="utf-8") as f:
        all_agents = json.load(f)

    agents = [agent for agent in all_agents if agent["role"] == role]
    return render_template("agent.html", map_id=map_id, side=side, role=role, agents=agents)

@app.route("/map/<map_id>/side/<side>/agent/<agent_id>")
def show_points_no_role(map_id, side, agent_id):
    with open("data/points.json", "r", encoding="utf-8") as f:
        all_points = json.load(f)

    points = [
        point for point in all_points
        if point["map"] == map_id and point["side"] == side and point["agent"] == agent_id
    ]

    return render_template("points.html", map_id=map_id, side=side, role=None, agent_id=agent_id, points=points)

@app.route("/point/<int:point_id>")
def point_detail(point_id):
    with open(POINTS_JSON, "r", encoding="utf-8") as f:
        points = json.load(f)

    point = next((p for p in points if p["id"] == point_id), None)
    if not point:
        return "定点が見つかりません", 404

    return render_template("point_detail.html", point=point)



if __name__ == "__main__":
    app.run(debug=True)
