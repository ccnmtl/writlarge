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
                    repositories: []
                };
            },
            methods: {
                onCreateRepository: function(event) {
                    const q = '.create-repository-form input[name="title"]';
                    const title = $(q).val();
                    const place = this.$children[0].getPlace();

                    this.addressError = !place;
                    this.titleError = !title;

                    if (this.addressError || this.titleError) {
                        return;
                    }

                    const params = {
                        url: WritLarge.baseUrl + 'api/repository/',
                        dataType: 'json',
                        contentType: 'application/json',
                        data: JSON.stringify({
                            'title': title,
                            'latlng': place.position.toJSON()
                        })
                    };

                    $.post(params, (response) => {
                        this.repositoryForm = false;
                        this.collectionForm = true;
                        $('select[name="repository"]').append(
                            $('<option></option>')
                                .attr('value', response.id)
                                .text(response.title));
                        $('select[name="repository"]').val(response.id);
                    });
                },
                onSelectRepository: function(event) {
                    const value = $(event.currentTarget).val();
                    this.repositoryForm = value && value === 'create';
                    this.collectionForm = value && value !== 'create';
                },
                hideForm: function(event) {
                    this.repositoryForm = false;
                }
            },
            created: function() {
                this.collectionForm = WritLarge.collectionForm;
            },
        });
    });
});

