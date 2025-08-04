@flask_app.route("/run_task", methods=["POST"])
def run_task():
    task_id = request.form.get("task_id")
    result = None
      # قبول البيانات سواء كانت JSON أو form-urlencoded
    if request.is_json:
        data = request.get_json()
        task_id = data.get("task_id")
    else:
        task_id = request.form.get("task_id")
    
    if not task_id:
        return jsonify(error="Missing task_id"), 400

    if task_id == "1":
        result = matrix_multiply(500)
    elif task_id == "2":
        result = prime_calculation(100_000)
    elif task_id == "3":
        result = data_processing(10_000)
    
    return jsonify(result=result)  # إرجاع JSON بدل HTML
