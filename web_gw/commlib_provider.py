from commlib.node import Node


class CommlibProvider:
    gnode: Node = None
    gpub = None

    def __init__(self):
        pass

    @staticmethod
    def init_commlib_node(broker: str, debug: bool = True):
        if broker == 'redis':
            from commlib.transports.redis import ConnectionParameters
        elif broker == 'amqp':
            from commlib.transports.amqp import ConnectionParameters
        elif broker == 'mqtt':
            from commlib.transports.mqtt import ConnectionParameters
        else:
            raise ValueError('Not a valid broker-type was given!')
        conn_params = ConnectionParameters()

        gnode = Node(
            node_name=f'http_to_{broker}_gw',
            connection_params=conn_params,
            debug=debug
        )
        gpub = CommlibProvider.init_global_publisher(gnode)
        CommlibProvider.gnode = gnode
        CommlibProvider.gpub = gpub
        print(f'Initiated {gnode}')
        print(f'Initiated {gpub}')

    @staticmethod
    def init_global_publisher(node):
        gpub = node.create_mpublisher()
        return gpub
