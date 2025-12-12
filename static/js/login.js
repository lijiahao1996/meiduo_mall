// static/js/login.js

var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host: typeof host !== 'undefined' ? host : '',
        error_username: false,
        error_password: false,
        error_username_message: '请输入5-20个字符的用户名',
        error_password_message: '请输入8-20位的密码',
        username: '',
        password: '',
        remembered: true
    },
    methods: {
        // 检查账号
        check_username: function () {
            var re1 = /^[a-zA-Z0-9_-]{5,20}$/;  // 用户名
            var re2 = /^1[3-9]\d{9}$/;          // 手机号

            if (re1.test(this.username) || re2.test(this.username)) {
                this.error_username = false;
            } else {
                this.error_username = true;
                this.error_username_message = "请输入正确的用户名或手机号";
            }
        },
        // 检查密码
        check_password: function () {
            var re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password_message = '密码必须是8-20位字母或数字';
                this.error_password = true;
            }
        },
        // 表单提交
        on_submit: function (event) {
            // 执行前端校验
            this.check_username();
            this.check_password();

            // 只要有一个错误，就阻止表单提交
            if (this.error_username || this.error_password) {
                event.preventDefault();
            }
            // 否则让表单正常提交，后端再做最终校验
        },
        // qq登录（暂时你后端没写可以先留着）
        qq_login: function () {
            var next = get_query_string('next') || '/';
            // 注意：host 里一般配置的是 http://www.meiduo.site:8000 或 http://localhost:8000
            var url = this.host + '/oauth/qq/login/?next=' + encodeURIComponent(next);
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    location.href = response.data.login_url;
                })
                .catch(error => {
                    console.log(error.response);
                });
        }
    }
});
