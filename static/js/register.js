// 创建 Vue 实例，管理整个注册页面
var vm = new Vue({
    el: '#app',   // Vue 绑定页面上 id="app" 的元素

    // 修改 Vue 的插值语法，避免和 Django/Jinja2 的 {{ }} 冲突
    delimiters: ['[[', ']]'],

    // ===== 页面数据 =====
    data: {
        host: host,  // 静态 host.js 定义的 API 域名
        // 错误标识
        error_name: false,
        error_password: false,
        error_password2: false,
        error_check_password: false,
        error_mobile: false,
        error_image_code: false,
        error_sms_code: false,
        error_allow: false,

        // 错误提示内容
        error_name_message: '请输入5-20个字符的用户',
        error_password_message: '请输入8-20位的密码',
        error_password2_message: '两次输入的密码不一致',
        error_mobile_message: '请输入正确的手机号码',
        error_image_code_message: '请填写图形验证码',
        error_sms_code_message: '请填写短信验证码',
        error_allow_message: '请勾选用户协议',

        // 验证码相关
        image_code_id: '',
        image_code_url: '',
        sms_code_tip: '获取短信验证码',
        sending_flag: false,   // 是否正在发送短信验证码（防止重复点击）

        // 表单字段
        username: '',
        password: '',
        password2: '',
        mobile: '',
        image_code: '',
        sms_code: '',
        allow: true
    },

    // Vue 生命周期：页面加载完自动执行
    mounted: function () {
        this.generate_image_code();   // 自动加载验证码图片
    },

    // ===== 方法区 =====
    methods: {

        // 生成唯一编号（UUID）——用于验证码 ID
        generateUUID: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now();
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },

        // 生成验证码 URL
        generate_image_code: function () {
            // 1. 每次生成新的 UUID
            this.image_code_id = this.generateUUID();

            // 2. 重新生成验证码 URL
            this.image_code_url = this.host + "/users/image_codes/" + this.image_code_id + "/";

            console.log("验证码URL:", this.image_code_url);
        },

        // 校验用户名格式 + 是否重复
        check_username: function () {
            // ① 如果为空，直接报错，不发请求
            if (!this.username) {
                this.error_name_message = '请输入用户名';
                this.error_name = true;
                return;   // ← 必须 return
            }

            // ② 检查格式
            var re = /^[a-zA-Z0-9_-]{5,20}$/;
            if (!re.test(this.username)) {
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
                return;   // ← 格式不对也不能发请求
            }

            // ③ 格式正确，先取消错误
            this.error_name = false;

            // ④ 再发送 AJAX 请求检查是否重复
            var url = this.host + "/users/usernames/" + this.username + "/count/";

            axios.get(url, { responseType: "json" })
                .then(response => {
                    if (response.data.count > 0) {
                        this.error_name_message = "用户名已存在";
                        this.error_name = true;
                    } else {
                        this.error_name = false;
                    }
                })
                .catch(error => {
                    console.log(error);
                    this.error_name_message = "服务器异常";
                    this.error_name = true;
                });
        },


        // 校验密码格式
        check_password: function () {
            var re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },

        // 校验重复密码
        check_password2: function () {
            if (this.password != this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },

        // 校验手机号格式
        check_mobile: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }
        },


        // 校验图片验证码是否为空
        check_image_code: function () {

            if (!this.image_code) {
                this.error_image_code_message = '请填写图片验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },




        // 校验短信验证码是否为空
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },

        // 是否同意用户协议
        check_allow: function () {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },

        // 点击按钮发送短信验证码
        send_sms_code: function () {

            if (this.sending_flag == true) return;

            this.sending_flag = true;

            // 输入校验
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile || this.error_image_code) {
                this.sending_flag = false;
                return;
            }

            // 构造短信验证码 API URL
            var url = this.host + '/sms_codes/' + this.mobile +
                      '/?image_code=' + this.image_code +
                      '&image_code_id=' + this.image_code_id;

            // 发送请求
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    // 成功
                    if (response.data.code == '0') {
                        var num = 60;
                        var t = setInterval(() => {
                            if (num == 1) {
                                clearInterval(t);
                                this.sms_code_tip = '获取短信验证码';
                                this.sending_flag = false;
                            } else {
                                num -= 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000);
                    }
                    // 后端错误
                    else {
                        if (response.data.code == '4001') {
                            this.error_image_code_message = response.data.errmsg;
                            this.error_image_code = true;
                        } else {
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.generate_image_code();
                        this.sending_flag = false;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.sending_flag = false;
                });
        },

        // 表单提交前最终校验
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_allow();

            if (
                this.error_name || this.error_password || this.error_check_password ||
                this.error_mobile || this.error_sms_code || this.error_allow
            ) {
                // 阻止表单提交
                window.event.returnValue = false;
            }
        }
    }
});
