var vm = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        host,
        is_show_edit: false,

        // 省市区数据
        provinces: [],
        cities: [],
        districts: [],

        // 地址列表
        addresses: [],
        default_address_id: null,

        // 编辑状态
        editing_address_index: '',

        // 表单数据
        form_address: {
            title: '',
            receiver: '',
            province_id: '',
            city_id: '',
            district_id: '',
            place: '',
            mobile: '',
            tel: '',
            email: '',
        }
    },

    mounted() {
        // Django 注入的数据
        this.addresses = JSON.parse(JSON.stringify(addresses));
        this.default_address_id = default_address_id;

        // 加载省份
        this.get_provinces();
    },

    watch: {
        // 省 -> 市
        'form_address.province_id'(val) {
            if (!val) {
                this.cities = [];
                this.districts = [];
                return;
            }
            axios.get(this.host + '/areas/?area_id=' + val)
                .then(res => {
                    if (res.data.code === '0') {
                        this.cities = res.data.sub_data;
                        this.districts = [];
                    }
                });
        },

        // 市 -> 区
        'form_address.city_id'(val) {
            if (!val) {
                this.districts = [];
                return;
            }
            axios.get(this.host + '/areas/?area_id=' + val)
                .then(res => {
                    if (res.data.code === '0') {
                        this.districts = res.data.sub_data;
                    }
                });
        }
    },

    methods: {
        // 获取省份
        get_provinces() {
            axios.get(this.host + '/areas/')
                .then(res => {
                    if (res.data.code === '0') {
                        this.provinces = res.data.province_list;
                    }
                });
        },

        // 显示新增弹窗
        show_add_site() {
            this.is_show_edit = true;
            this.editing_address_index = '';

            this.form_address = {
                title: '',
                receiver: '',
                province_id: '',
                city_id: '',
                district_id: '',
                place: '',
                mobile: '',
                tel: '',
                email: '',
            };

            this.cities = [];
            this.districts = [];
        },

        // 显示编辑弹窗
        show_edit_site(index) {
            this.is_show_edit = true;
            this.editing_address_index = index;

            // 深拷贝，避免污染原数据
            this.form_address = JSON.parse(JSON.stringify(this.addresses[index]));

            // 回显省市区
            axios.get(this.host + '/areas/?area_id=' + this.form_address.province_id)
                .then(res => {
                    this.cities = res.data.sub_data;
                });

            axios.get(this.host + '/areas/?area_id=' + this.form_address.city_id)
                .then(res => {
                    this.districts = res.data.sub_data;
                });
        },

        // 保存地址（新增 / 修改）
        save_address() {
            let url;
            let method;

            // ===== 新增地址 =====
            if (this.editing_address_index === '') {
                url = this.host + '/users/addresses/create/';
                method = 'post';
            }
            // ===== 编辑地址 =====
            else {
                url = this.host + '/users/addresses/' +
                      this.addresses[this.editing_address_index].id + '/';
                method = 'put';
            }

            // title 默认等于 receiver
            this.form_address.title = this.form_address.receiver;

            axios({
                url: url,
                method: method,
                data: this.form_address,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            }).then(res => {
                if (res.data.code === 0) {
                    if (method === 'post') {
                        // 新增
                        this.addresses.unshift(res.data.address);
                    } else {
                        // 修改
                        this.$set(
                            this.addresses,
                            this.editing_address_index,
                            res.data.address
                        );
                    }
                    this.is_show_edit = false;
                } else {
                    alert(res.data.errmsg || '操作失败');
                }
            });
        },

        // 删除地址
        delete_address(index) {
            axios.delete(
                this.host + '/users/addresses/' + this.addresses[index].id + '/',
                {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                }
            ).then(res => {
                if (res.data.code === 0) {
                    this.addresses.splice(index, 1);
                } else {
                    alert(res.data.errmsg || '删除失败');
                }
            });
        },

        // 设置默认地址
        set_default(index) {
            axios.put(
                this.host + '/users/addresses/' + this.addresses[index].id + '/default/',
                {},
                {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                }
            ).then(res => {
                if (res.data.code === 0) {
                    this.default_address_id = this.addresses[index].id;
                } else {
                    alert(res.data.errmsg || '设置失败');
                }
            });
        }
    }
});
