/* global GoogleMapVue:true, ExtendedDateVue: true, csrfSafeMethod:true */

requirejs(['./common'], function() {
    const a = ['jquery', 'utils', 'bootstrap', 'Vue', 'mapVue', 'edtfVue'];
    requirejs(a, function($, utils, bootstrap, Vue, mapVue, edtfVue) {

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
                'edtf': ExtendedDateVue
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

                    const data = {
                        'title': this.repositoryTitle,
                        'place': {
                            'title': this.$children[0].getSearchTerm(),
                            'latlng': place.position.toJSON()
                        }
                    };

                    const params = {
                        url: WritLarge.baseUrl + 'api/repository/',
                        dataType: 'json',
                        contentType: 'application/json',
                        data: JSON.stringify(data)
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
                },
                onSubmit: function(event) {
                    for (let i=0; i < this.$children.length; i++) {
                        if (this.$children[i].errors > 0) {
                            this.$children[i].setFocus();
                            event.preventDefault();
                            event.stopPropagation();
                            break;
                        }
                    }
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

