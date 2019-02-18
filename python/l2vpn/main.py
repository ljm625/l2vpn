# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


def getIpAddress(addr):
    """Return the Ip part of a 'Ip/Net' string."""
    parts = addr.split('/')
    return parts[0]


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        # TODO: Add auto fill for loopback ip
        # TODO: Resource Manager for pw-id

        pw_id = service.pw_id

        endpoint1 = service.endpoint1
        endpoint2 = service.endpoint2
        interface1 = endpoint1.interface
        lb_ip1 = getIpAddress(endpoint1.loopback_ip)
        interface2 = endpoint2.interface
        lb_ip2 = getIpAddress(endpoint2.loopback_ip)

        vars = ncs.template.Variables()
        vars.add("DEVICE_NAME",endpoint1.name)
        vars.add("INTF_NUMBER",interface1)
        vars.add("L2VPN_NAME",service.name)
        vars.add("P2P_NAME",endpoint1.name+"_to_"+endpoint2.name)
        vars.add("PEER_LOOPBACK",lb_ip2)
        vars.add("PWID",pw_id)

        vars2 = ncs.template.Variables()
        vars2.add("DEVICE_NAME", endpoint2.name)
        vars2.add("INTF_NUMBER", interface2)
        vars2.add("L2VPN_NAME", service.name)
        vars2.add("P2P_NAME", endpoint1.name + "_to_" + endpoint2.name)
        vars2.add("PEER_LOOPBACK", lb_ip1)
        vars2.add("PWID", pw_id)

        template = ncs.template.Template(service)
        template.apply('l2vpn-iosxr', vars)

        template2 = ncs.template.Template(service)
        template2.apply('l2vpn-iosxr', vars2)

        # vars = ncs.template.Variables()
        # vars.add('DUMMY', '127.0.0.1')
        # template = ncs.template.Template(service)
        # template.apply('l2vpn-template', vars)

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_lock_create
    # def cb_pre_lock_create(self, tctx, root, service, proplist):
    #     self.log.info('Service plcreate(service=', service._path, ')')

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Started l2vpn')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('l2vpn-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
