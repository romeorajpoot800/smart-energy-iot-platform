from flask import Blueprint, request, jsonify
from database.db import add_device, get_user_devices, remove_device, insert_sensor, get_device_logs

device_bp = Blueprint("device_bp", __name__)


@device_bp.route("/device/add", methods=["POST"])
def add_new_device():

    data = request.json

    user_id = data.get("user_id")
    device_name = data.get("device_name")
    mac_address = data.get("mac_address")

    if not user_id or not mac_address:
        return jsonify({"error": "missing_fields"})

    success = add_device(user_id, device_name, mac_address)

    if success:
        return jsonify({"status": "device_added"})
    else:
        return jsonify({"error": "device_exists"})


@device_bp.route("/device/list/<int:user_id>", methods=["GET"])
def list_devices(user_id):

    devices = get_user_devices(user_id)

    result = []

    for d in devices:
        result.append({
            "device_name": d[0],
            "mac_address": d[1]
        })

    return jsonify({"devices": result})


@device_bp.route("/device/remove", methods=["DELETE"])
def delete_device():

    data = request.json
    mac = data.get("mac_address")

    if not mac:
        return jsonify({"error": "mac_required"})

    remove_device(mac)

    return jsonify({"status": "device_removed"})


@device_bp.route("/energy/data", methods=["POST"])
def receive_energy_data():

    data = request.json

    mac = data.get("mac_address")
    voltage = data.get("voltage")
    current = data.get("current")
    power = data.get("power")

    if not mac:
        return jsonify({"error": "mac_required"})

    insert_sensor(mac, voltage, current, power)

    return jsonify({"status": "energy_logged"})


@device_bp.route("/energy/logs/<mac>", methods=["GET"])
def get_logs(mac):

    logs = get_device_logs(mac)

    result = []

    for row in logs:
        result.append({
            "voltage": row[0],
            "current": row[1],
            "power": row[2],
            "timestamp": row[3]
        })

    return jsonify({"logs": result})