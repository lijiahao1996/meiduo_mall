var vm = new Vue({
    el: '#app',
    // 避免与 Django 模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host: host,

        // 后端注入的初始数据
        username: username,
        mobile: mobile,
        email: email,
        email_active: email_active,

        // 页面状态控制
        set_email: false,

        // 邮箱校验状态
        error_email: false,
        error_email_message: '',

        // 发送按钮状态
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',

        // 浏览记录
        histories: []
    },

    mounted() {
        // 处理后端传来的字符串 True / False
        this.email_active = (this.email_active === 'True' || this.email_active === true);

        // 如果没有邮箱，进入编辑状态
        this.set_email = !this.email;

        // ❌ 初始化阶段不做任何邮箱校验（非常重要）
        this.error_email = false;
        this.error_email_message = '';

        // 浏览记录（等你后面打开）
        // this.browse_histories();
    },

    methods: {

        /**
         * 校验邮箱格式
         * 只在【保存】或【失焦】时调用
         */
        check_email() {
            // 空值不校验（防止初始化就报错）
            if (!this.email) {
                this.error_email = false;
                this.error_email_message = '';
                return true;
            }

            var re = /^[a-z0-9][\w.-]*@[a-z0-9-]+(\.[a-z]{2,5}){1,2}$/;

            if (!re.test(this.email)) {
                this.error_email_message = '邮箱格式错误';
                this.error_email = true;
                return false;
            }

            // 校验通过，清空错误
            this.error_email = false;
            this.error_email_message = '';
            return true;
        },

        /**
         * 取消编辑邮箱
         */
        cancel_email() {
            this.email = '';
            this.error_email = false;
            this.error_email_message = '';
            this.set_email = true;
        },

        /**
         * 保存邮箱
         */
        save_email() {
            // 先校验
            if (!this.check_email()) {
                return;
            }

            var url = this.host + '/users/emails/';

            axios.put(
                url,
                { email: this.email },
                {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    responseType: 'json'
                }
            )
            .then(response => {
                if (response.data.code === '0') {
                    // 保存成功
                    this.set_email = false;
                    this.send_email_btn_disabled = true;
                    this.send_email_tip = '已发送验证邮件';
                } else if (response.data.code === '4101') {
                    // 未登录
                    location.href = '/users/login/?next=/users/center/';
                } else {
                    // 其他错误
                    this.error_email_message = response.data.errmsg;
                    this.error_email = true;
                }
            })
            .catch(error => {
                console.log(error);
            });
        },

        /**
         * 获取浏览历史（后面用）
         */
        browse_histories() {
            var url = this.host + '/browse_histories/';

            axios.get(url, { responseType: 'json' })
                .then(response => {
                    this.histories = response.data.skus;
                    for (var i = 0; i < this.histories.length; i++) {
                        this.histories[i].url = '/goods/' + this.histories[i].id + '.html';
                    }
                })
                .catch(error => {
                    console.log(error);
                });
        }
    }
});
