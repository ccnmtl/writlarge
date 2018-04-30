/* global d3: true */
/* exported FamilyNetworkVue */

var FamilyNetworkVue = {
    props: ['siteid'],
    template: '#family-network',
    data: function() {
        return {
            networkName: 'the-network',
            site: null,
            complete: false
        };
    },
    methods: {
        getNodeColor: function(node) {
            return 'gray';
        },
        buildDiagram: function() {
            const elt = document.getElementById(this.networkName);
            const width = elt.clientWidth;
            const height = 300;
            let nodes = this.site.family;
            nodes.unshift({
                'id': this.site.id,
                'title': this.site.title,
                'group': this.site.category[0].group,
                'relationship': 'self'
            });

            var svg = d3.select('svg');
            svg.attr('width', width).attr('height', height);

            // http://d3indepth.com/force-layout/
            var simulation = d3
                .forceSimulation()
                .force('charge', d3.forceManyBody().strength(-30))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force("xPosition", d3.forceY(function(d){
                    return d.relationship === 'antecedent' ?  : d.x
                }).strength(2))

            var nodeElements = svg.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(nodes)
                .enter().append('circle')
                .attr('r', 15)
                .attr('fill', this.getNodeColor);

            var textElements = svg.append('g')
                .attr('class', 'texts')
                .selectAll('text')
                .data(nodes)
                .enter().append('text')
                .text(function(node) { return node.title; })
                .attr('font-size', 15)
                .attr('dx', 20)
                .attr('dy', 4);

            simulation.nodes(this.site.family).on('tick', () => {
                nodeElements
                    .attr('cx', function(node) { return node.x; })
                    .attr('cy', function(node) { return node.y; });
                textElements
                    .attr('x', function(node) { return node.x; })
                    .attr('y', function(node) { return node.y; });
            });
            this.complete = true;
        }
    },
    created: function() {
        const url = WritLarge.baseUrl + 'api/site/' +  this.siteid + '/';
        jQuery.getJSON(url, (data) => {
            this.site = data;
        });
    },
    updated: function() {
        this.buildDiagram();
    }
};
