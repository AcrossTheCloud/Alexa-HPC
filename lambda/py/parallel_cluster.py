# -*- coding: utf-8 -*-

# This is a simple Hello World Alexa Skill, built using
# the implementation of handler classes approach in skill builder.
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

# use subprocess for now to talk to pcluster command
import subprocess

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Welcome to the Parallel Cluster skill, you can ask me to start a cluster, or to check the cluster, or to delete the cluster."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Parallel Cluster", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class StartHPCIntentHandler(AbstractRequestHandler):
    """Handler for Start HPC Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("StartHPCIntent")(handler_input)

    def handle(self, handler_input):

        speech_text = "Your cluster is starting." # default

        completed = subprocess.run(
            ['./pcluster-cli', 
                'create', 
                '-nw', 
                '-c', '.parallelcluster/config', 
                'myAlexaCluster'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )

        if completed.returncode != 0:
            speech_text = "Problem starting your cluster. " + \
                completed.stdout + " " + \
                completed.stderr

        print(completed.stdout)
        print(completed.stderr)
        
        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Parallel Cluster", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class HPCStatusIntentHandler(AbstractRequestHandler):
    """Handler for HPC Status Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("HPCStatusIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Your cluster is starting." # default

        completed = subprocess.run(
            ['./pcluster-cli',
                'status',
                '-nw',  # must use -nw here otherwise it will keep running and outputting until cluster created
                '-c', '.parallelcluster/config',
                'myAlexaCluster'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )

        print(completed.stdout)
        print(completed.stderr)

        if "DELETE_IN_PROGRESS" in completed.stdout:
            speech_text = "Your cluster is being deleted."

        if "does not exist" in completed.stdout:
            speech_text = "Your cluster has been deleted."
        
        if "CREATE_COMPLETE" in completed.stdout:
            completed = subprocess.run( # need to run again without -nw to get full listing for IP address
                ['./pcluster-cli',
                    'status', 
                    '-c', '.parallelcluster/config',
                    'myAlexaCluster'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            for line in completed.stdout.splitlines():
                if "MasterPublicIP" in line:
                    ip = line.split(": ")[1]
                    speech_text = 'Your cluster has started. The master node IP address is <say-as interpret-as="digits">'+ip+'</say-as>.'

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Parallel Cluster", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response


class DeleteHPCIntentHandler(AbstractRequestHandler):
    """Handler for Delete HPC Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("DeleteHPCIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Your cluster is being deleted." # default

        completed = subprocess.run(
            ['./pcluster-cli',
                'delete',
                '-nw',
                '-c', '.parallelcluster/config',
                'myAlexaCluster'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )

        if completed.returncode != 0:
            speech_text = "Problem deleting your cluster. " + \
                completed.stdout + " " + \
                completed.stderr

        print(completed.stdout)
        print(completed.stderr)

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Parallel Cluster", speech_text)).set_should_end_session(
            True)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can say say !"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard(
                "Parallel Cluster", speech_text))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Parallel Cluster", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Alexa Parallel Cluster skill can't help you with that.  "
            "You can ask me to start a cluster, check a cluster, or delete a cluster.")
        reprompt = "You can ask me to start a cluster, check cluster, or delete a cluster."
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again."
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StartHPCIntentHandler())
sb.add_request_handler(HPCStatusIntentHandler())
sb.add_request_handler(DeleteHPCIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

handler = sb.lambda_handler()
