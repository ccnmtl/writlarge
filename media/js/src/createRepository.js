/* global GoogleMapVue:true, csrfSafeMethod:true */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue', 'mapVue'];
    requirejs(a, function($, utils, bootstrap, Vue, mapVue) {

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    const token =
                        $('meta[name="csrf-token"]').attr('content');
                    xhr.setRequestHeader('X-CSRFToken', token);
                }
            }
        });

        new Vue({
            el: '#archival-collection-create',
            components: {
                'google-map': GoogleMapVue,
            },
            data: function() {
                return {
                    addressError: false,
                    titleError: false,
                    collectionForm: false,
                    repositoryForm: false,
                    repositories: [],
                    selectedRepository: '',
                    repositoryTitle: ''
                };
            },
            watch: {
                selectedRepository: function(value) {
                    this.repositoryForm = value && value === 'create';
                    this.collectionForm = value && value !== 'create';
                }
            },
            methods: {
                onCreateRepository: function(event) {
                    const place = this.$children[0].getPlace();
                    this.addressError = !place;
                    this.titleError = !this.repositoryTitle;

                    if (this.addressError || this.titleError) {
                        return;
                    }

                    const params = {
                        url: WritLarge.baseUrl + 'api/repository/',
                        dataType: 'json',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            'title': this.repositoryTitle,
                            'latlng': place.position.toJSON()
                        })
                    };

                    $.post(params, (response) => {
                        this.repositoryForm = false;
                        this.collectionForm = true;
                        this.repositories.push({
                            'id': response.id, 'title': response.title
                        });
                        this.selectedRepository = response.id;
                    });
                },
                hideForm: function(event) {
                    this.repositoryForm = false;
                }
            },
            created: function() {
                this.collectionForm = WritLarge.collectionForm;
                this.repositories = WritLarge.repositories;
                this.selectedRepository = WritLarge.repository;
            }
        });
    });
});

