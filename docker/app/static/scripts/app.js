
function set_terminal_url () {
    let terminal_port = ':57575',
        protocol = window.location.protocol,
        hostname = window.location.hostname,
        src = protocol + '//' + hostname + terminal_port,
        terminal = $('#fut_terminal')
    console.log('Setting terminal url - ' + src)
    terminal.attr('src', src)
}

$(function() {
    set_terminal_url()
});

function show_tab (show_tab) {
    let tabs = ['fut_terminal_tab', 'allure_tab', 'fut_setup_tab']
    $.each(tabs, function(tab_index, tab_name) {
        let tab = $('#' + tab_name);
        if (show_tab === tab_name) {
            tab.removeClass('hidden');
        } else {
            tab.addClass('hidden');
        }
    });
}

function get_builds () {
    $.getJSON("/get_builds", function(data) {
        var items = [];
        $.each(data.data, function(key, val) {
            items.push(
                "<div class=\"build_div_wrapper\">" +
                    "<div class=\"build_div_link_wrapper\">" +
                        "<a href='#' onclick='get_allure(\"" + val + "\", \"False\")'>" + val + "</a>" +
                    "</div>" +
                    "<div class=\"build_div_tools_wrapper\">" +
                        "<a href='#' onclick='get_allure(\"" + val + "\", \"True\")'><img alt=\"Rebuild\" src=\"/static/extras/arrow-repeat.png\"></a>" +
                        "<a href='/download_allure?build_name=" + val + "' target=_blank><img alt=\"Download\" src=\"/static/extras/arrow-down-circle.png\"></a>" +
                        "<a href='#' onclick='delete_allure(\"" + val + "\")'><img alt=\"Delete\" src=\"/static/extras/trash.png\"></a>" +
                    "</div>" +
                "</div>"
            );
        });
        $('#fut_build_list').html(items.join(''))
    });
}

function get_allure (build_name, rebuild) {
    hide_nav('fut_builds_nav')
    let loader = $('#loader');
    loader.removeClass('hidden');
    $.getJSON("/get_allure?build_name=" + build_name + "&rebuild=" + rebuild, function(data) {
        if (data.success !== true) {
            alert(data.data)
            loader.addClass('hidden')
        } else {
            let allure_iframe = $('#allure_iframe');
            allure_iframe.on("load", function() {
                loader.addClass('hidden')
            });
            console.log('Loading allure report - ' + data.url)
            allure_iframe.attr('src', data.url)
        }
    });
}

function delete_allure (build_name) {
    $.getJSON("/delete_allure?build_name=" + build_name, function(data) {
        if (data.success !== true) {
            alert(data.data)
        } else {
            get_builds()
        }
    });
}

function get_env () {
    $.getJSON("/get_env", function(data) {
        if (data.success !== true) {
            alert(data.data)
        } else {
            let env_info_table = $('#fut_env_table'),
                env_info_html = '<tr><th>Variable</th><th>Value</th></tr>';
            $.each(data.data, function(key, val) {
                env_info_html +=
                '<tr>' +
                    '<td>' + key + '</td>' +
                    '<td><input type="text" size="30" value="' + val + '"/></td>' +
                '</tr>';
            })
            env_info_table.html(env_info_html)
        }
    });
}

function set_env () {
    let env_info_table = $('#fut_env_table'),
        env_rows = $(env_info_table).find('> tr').slice(1),
        env_data = {};

    $.each(env_rows, function(i, el) {
        let env_name = $(el).find('td')[0].innerHTML,
            env_value = $(el).find('input')[0].value;
        if (env_value !== '' && env_value !== 'null') {
            env_data[env_name] = env_value;
        }
    });
    if ($.isEmptyObject(env_data)) {
        return false;
    }
    $.post('/set_env', env_data, function(data, textStatus) {
        //data contains the JSON object
        //textStatus contains the status: success, error, etc
    }, "json");
}

function show_nav (nav_name) {
    if (nav_name === 'fut_builds_nav') {
        get_builds()
    }
    $('#' + nav_name).removeClass('hide_tr')
}

function hide_nav (nav_name) {
    $('#' + nav_name).addClass('hide_tr')
}
