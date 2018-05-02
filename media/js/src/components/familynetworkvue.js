/* global d3: true */
/* exported FamilyNetworkVue */

var FamilyNetworkVue = {
    props: ['siteid'],
    template: '#family-network',
    data: function() {
        return {
            networkName: 'the-network',
            site: null,
            complete: false,
            iconSize: 24,
            patterns: {},
            nodes: [],
            edges: []
        };
    },
    methods: {
        getNodeImage: function(group) {
            return WritLarge.staticUrl + 'png/pin-' + group + '.png';
        },
        getXPosition: function(node, center) {
            if (node.relationship === 'self' ||
                    node.relationship === 'associate') {
                return center;
            } else if (node.relationship == 'antecedent') {
                return center / 4;
            } else {
                return center + center / 2;
            }
        },
        getYPosition: function(node, height) {
            if (node.relationship === 'associate') {
                return height / 2 + height / 4;
            } else {
                return height / 2;
            }
        },
        clearDiagram: function() {
            if (this.simulation) {
                d3.select('svg').selectAll('*').remove();
                this.simulation.nodes(this.nodes).on('tick', null);
                delete this.simulation;
            }
        },
        createPatterns: function(svg) {
            let defs = svg.append('svg:defs');
            for (let group in this.patterns) {
                if (this.patterns.hasOwnProperty(group)) {
                    defs.append('svg:pattern')
                        .attr('id', group)
                        .attr('height','100%')
                        .attr('width', '100%')
                        .append('svg:image')
                        .attr('xlink:href', this.patterns[group])
                        .attr('width', this.iconSize)
                        .attr('height', this.iconSize)
                        .attr('x', 0)
                        .attr('y', 0);
                }
            }
        },
        buildDiagram: function() {
            const self = this;
            this.clearDiagram();

            const elt = document.getElementById(this.networkName);
            const width = elt.clientWidth;
            const center = width / 2;
            const height = 200;

            let svg = d3.select('svg');
            svg.attr('width', width).attr('height', height);

            this.createPatterns(svg);

            const linkForce = d3
                .forceLink()
                .id(function(link) { return link.id; })
                .strength(function(link) { return .1; });

            this.simulation = d3
                .forceSimulation(this.nodes)
                .force('link', linkForce)
                .force('charge', d3.forceManyBody().strength(-400))
                .force('center', d3.forceCenter(center, height / 2))
                .force('y', d3.forceY().y(function(d) {
                    return self.getYPosition(d, height);
                }))
                .force('x', d3.forceX().x(function(d) {
                    return self.getXPosition(d, center);
                }));

            const linkElements = svg.append('g')
                .attr('class', 'links')
                .selectAll('line')
                .data(this.edges)
                .enter().append('line')
                .attr('stroke-width', 1)
                .attr('stroke', 'rgba(50, 50, 50, 0.2)');

            const nodeElements = svg.append('g')
                .attr('class', 'nodes')
                .selectAll('circle')
                .data(this.nodes)
                .enter().append('circle')
                .attr('r', this.iconSize / 2)
                .style('fill', function(node) {
                    return 'url(#' + node.group + ')';
                });

            const textElements = svg.append('g')
                .attr('class', 'texts')
                .selectAll('text')
                .data(this.nodes)
                .enter().append('text')
                .text(function(node) { return node.title; })
                .attr('font-size', 15)
                .attr('dx', function(node) {
                    return -node.title.length * 7 / 2; })
                .attr('dy', -20);

            this.simulation.nodes(this.nodes).on('tick', function(node) {
                nodeElements
                    .attr('cx', function(node) { return node.x; })
                    .attr('cy', function(node) { return node.y; });
                textElements
                    .attr('x', function(node) { return node.x; })
                    .attr('y', function(node) { return node.y; });
                linkElements
                    .attr('x1', function(link) { return link.source.x; })
                    .attr('y1', function(link) { return link.source.y; })
                    .attr('x2', function(link) { return link.target.x; })
                    .attr('y2', function(link) { return link.target.y; });
            });

            this.simulation.force('link').links(this.edges);
        }
    },
    created: function() {
        const url = WritLarge.baseUrl + 'api/site/' +  this.siteid + '/';
        jQuery.getJSON(url, (data) => {
            this.nodes = data.family;
            this.nodes.unshift({
                'id': data.id,
                'title': data.title,
                'group': data.category[0].group,
                'relationship': 'self'
            });
            for (let node of this.nodes) {
                const group = node.group;
                if (!(group in this.patterns)) {
                    this.patterns[group] = this.getNodeImage(group);
                }

                if (node.relationship !== 'self') {
                    this.edges.push({source: data.id, target: node.id });
                }
            }
            this.site = data;
        });
    },
    mounted: function() {
        // eslint-disable-next-line scanjs-rules/call_addEventListener
        window.addEventListener('resize', this.buildDiagram);
    },
    updated: function() {
        this.buildDiagram();
    }
};
