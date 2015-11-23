$(document).ready(function() {
	function pad(num) {
		if (num < 10)
			return "0" + num;
		else
			return num + "";
	}

	function load_student(id, quiz_index, total_quizzes, student_name) {
		var dialog_content;
		var url_prefix = $("#site_url").val() + "students/";
		$.ajax({
			type: "GET",
			dataType: "json",
			url: url_prefix + id.toString() + "/quizzes/" + quiz_index.toString() + "/",
			success: function(data) {
				if (!$.isEmptyObject(data)) {
					$("#st-quiz-name").text(data.annal);
					$("#st-quiz-submitted").text(data.submitted);
					$("#st-quiz-score").text(data.score);
					$("#st-quiz-nb-questions").text(data.number_of_questions);
					$("#st-quiz-started").text(data.start_time);
					$("#st-quiz-finished").text(data.finish_time);
					$("#st-quiz-total").text(total_quizzes);
					$("#st-quiz-current").text(quiz_index + 1);
					$(".pager-previous").attr("tag", data.student_id);
					$(".pager-next").attr("tag", data.student_id);
					if (!(typeof student_name === "undefined")) {
						$("#st-panel-subtitle").text(student_name.toString());
						$("#st-panel-title").show();
					}
					$("#table-quizzes").show();
				}
			},
		});
	}

	var msg_student_name_required = $("#msg-student-name-required").val();
	var msg_annal_name_required = $("#msg-annal-name-required").val();
	var msg_annal_duration_required = $("#msg-annal-duration-required").val();

	$(".selectpicker").selectpicker();
	$(".datetimebox").datetimepicker({locale: "en"});

	$(".bs_switch").bootstrapSwitch();

	$("#select-locale").change(function() {
		$("#locale-hidden").val($("#select-locale").find("option:selected").val());
		$("#form-change-locale").submit();
	});

	$("#navbar-rules").click(function() {
		var rules = $("#rules-hidden").attr("value") || "No rules.";
		var rules_title = $("#rules-title-hidden").attr("value");
		var dialog_close = $("#close-hidden").attr("value");
		bootbox.dialog({
			title: rules_title,
			message: rules,
			buttons: {
				main: {
					label: dialog_close,
					className: "btn-primary"
				}
			}
		});
	});

	$("#annal_starts_on_checkbox").on("switchChange.bootstrapSwitch", function(event, state) {
		$("#annal_starts_on_text").prop("disabled", !state);
	});

	$("#annal_ends_on_checkbox").on("switchChange.bootstrapSwitch", function(event, state) {
		$("#annal_ends_on_text").prop("disabled", !state);
	});

	$(".student-nb-quizzes").click(function() {
		var student_id = parseInt($(this).attr("tag"));
		var current_index = parseInt($(this).attr("tag-current")) || 0;
		load_student(student_id, current_index, $(this).text(), $(this).attr("tag-student"));
	});

	$(".pager-previous").click(function() {
		var student_id = parseInt($(this).attr("tag"));
		var current_index = (parseInt($("#st-quiz-current").text()) - 1) || 0;
		if (current_index > 0)
			current_index--;
		load_student(student_id, current_index, $("#st-quiz-total").text());
	});

	$(".pager-next").click(function() {
		var student_id = parseInt($(this).attr("tag"));
		var current_index = (parseInt($("#st-quiz-current").text()) - 1) || 0;
		if (current_index < 0)
			current_index = 0;
		else
			current_index++;
		load_student(student_id, current_index, $("#st-quiz-total").text());
	});

	$("#form-change-student").bootstrapValidator({
		feedbackIcons: {
			valid: "glyphicon glyphicon-ok",
			invalid: "glyphicon glyphicon-remove",
			validating: "glyphicon glyphicon-refresh"
		},
		fields: {
			student_name: {
				validators: {
					notEmpty: {
						message: msg_student_name_required
					}
				}
			}
		}
	});

	$("#form-change-annal").bootstrapValidator({
		feedbackIcons: {
			valid: "glyphicon glyphicon-ok",
			invalid: "glyphicon glyphicon-remove",
			validating: "glyphicon glyphicon-refresh"
		},
		fields: {
			annal_name: {
				validators: {
					notEmpty: {
						message: msg_annal_name_required
					}
				}
			},
			annal_duration: {
				validators: {
					notEmpty: {
						message: msg_annal_duration_required
					}
				}
			}
		}
	});

	$(".checkbox_button").change(function() {
		var disabled_caption = $("#disabled_caption").val();
		var enabled_caption = $("#enabled_caption").val();
		var reveal_caption = $("#reveal_caption").val();
		var no_reveal_caption = $("#no_reveal_caption").val();
		if ($(this).is(":checked")) {
			$(this).parent().removeClass("btn-default");
			$(this).parent().addClass("btn-primary");
			if ($(this).attr("id") == "annal_reveal_answers")
				$(this).parent().find(".checkbox_caption").text(reveal_caption);
			else
				$(this).parent().find(".checkbox_caption").text(enabled_caption);
		}
		else {
			$(this).parent().removeClass("btn-primary");
			$(this).parent().addClass("btn-default");
			if ($(this).attr("id") == "annal_reveal_answers")
				$(this).parent().find(".checkbox_caption").text(no_reveal_caption);
			else
				$(this).parent().find(".checkbox_caption").text(disabled_caption);
		}
	});

	$("#add-student").click(function() {
		$("#student-action").val("add");
		$("#modal-change-student-title").text($("#student-add-title").val());
	});

	$("#add-annal").click(function() {
		$("#annal-action").val("add");
		$("#modal-change-annal-title").text($("#annal-add-title").val());
	});

	$("#delete-selected").click(function() {
		var confirm_yes = $("#confirm-yes").attr("value");
		var confirm_no = $("#confirm-no").attr("value");
		var confirm_title = $("#confirm-title").attr("value");
		var confirm_message = $("#confirm-message").attr("value");
		bootbox.dialog({
			title: confirm_title,
			message: confirm_message,
			buttons: {
				yes: {
					label: confirm_yes,
					className: "btn-danger",
					callback: function () {
						$("#changelist-action").val("delete");
						$("#changelist-form").submit();
					}
				},
				no: {
					label: confirm_no,
					className: "btn-default"
				}
			}
		});
	});

	$(".student-edit").click(function() {
		var stud_name = $.trim($(this).text());
		$("#student-action").val("edit");
		$("#modal-change-student-title").text($("#student-edit-title").val() + stud_name);
		$("#student_id").val($(this).attr("tag"));
		$("#student_name").val(stud_name);
	});

	$(".answers").click(function() {
		if ($(this).hasClass("yellow")) {
			$(this).removeClass("yellow");
			$(this).parent().find(".chosen-answer").val("");
		} 
		else {
			var question_id = ($(this).parent().attr("id")).substring(8);
			var answer_id = ($(this).attr("id")).substring(6);
			$(".answer-q" + question_id).removeClass("yellow");
			$(this).addClass("yellow");
			$(this).parent().find(".chosen-answer").val(answer_id);
		}		
	});

	$("#submit-button").click(function() {
		$("#form-submit").submit();
	});

	$("#student-search-icon").click(function() {
		$("#form-search-student").submit();
	});

	$("#student-remove-search").click(function() {
		window.location.href = $("#site_url").val() + "students/";
	});

	$("#login-success-alert").fadeIn();
	$("#login-success-alert").delay(4000).fadeOut();

	$("#alert-message").fadeIn();
	$("#alert-message").delay(4000).fadeOut();

	$("#sel-toggle-all").change(function() {
		if (this.checked)
			$(".sel-item").prop("checked", true);
		else
			$(".sel-item").prop("checked", false);
	});

	// for countdown timer in quizzes
	var timer = setInterval(function() {
		var ending_soon = false;
		var remaining_time = parseInt($("#remaining-time-hidden").attr("value"));
		if (remaining_time <= 0) {
			clearInterval(timer);
			$("#form-submit").submit();
		}
		else {
			var display_time = "";
			var hours;
			var minutes;
			var seconds;
			remaining_time--;
			if (remaining_time <= 30)
				ending_soon = true;
			else
				ending_soon = false;
			if (ending_soon) {
				$(".circle").css("background", "linear-gradient(135deg, #f85032 0%,#f16f5c 50%,#f6290c 51%,#f02f17 71%,#e73827 100%)");
				$(".circle-border").css("border", "3px solid #882222");
			}
			if (remaining_time < 60) {
				seconds = remaining_time.toString();
				display_time = seconds;
			}
			else if (remaining_time < 3600) {
				minutes = Math.floor(remaining_time / 60);
				seconds = remaining_time % 60;
				display_time = pad(minutes) + ":" + pad(seconds);
			}
			else {
				hours = Math.floor(remaining_time / 3600);
				minutes = Math.floor((remaining_time - hours * 3600) / 60);
				seconds = remaining_time % 60;
				display_time = hours + ":" + pad(minutes) + ":" + pad(seconds);
			}
			$("#remaining-time-hidden").val(remaining_time.toString());
			$(".time-text").text(display_time);
		}
	}, 1000);
});
