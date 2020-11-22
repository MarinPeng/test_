# -*- coding: utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _

from pipeline.core.flow.activity import Service
from pipeline.component_framework.component import Component
from gcloud.conf import settings
from selenium import webdriver
from faker import Faker

logger = logging.getLogger('celery')
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER

__group_name__ = _(u"自定义插件(CUSTOM)")


class TestCustomService(Service):
    __need_schedule__ = False

    def execute_pre_process(self, data, parent_data):
        test_input = data.inputs.test_input
        if not test_input.startswith("test_"):
            # message = "test_input should start with 'test_'"
            faker = Faker("zh_CN")
            message = "test_input should start with 'test_', fake: {}".format(faker.name())
            data.set_outputs('ex_data', message)
            return False
        return True
        
    def execute(self, data, parent_data):
        executor = parent_data.inputs.executor
        biz_cc_id = parent_data.inputs.biz_cc_id
        client = get_client_by_user(executor)

        test_input = data.inputs.test_input
        test_textarea = data.inputs.test_textarea
        test_radio = data.inputs.test_radio

        api_kwargs = {
            'biz_biz_id': biz_cc_id,
            'executor': executor,
            'test_input': test_input,
            'test_textarea': test_textarea,
            'test_radio': test_radio,
        }

        api_result = client.test_api.test1(api_kwargs)
        logger.info('test_api result: {result}, api_kwargs: {kwargs}'.format(result=api_result, kwargs=api_kwargs))
        if api_result['result']:
            data.set_outputs('data1', api_result['data']['data1'])
            return True
        else:
            data.set_outputs('ex_data', api_result['message'])
            return False

    def outputs_format(self):
        return [
            self.OutputItem(name=_(u'结果数据1'), key='data1', type='string')
        ]


class TestCustomComponent(Component):
    name = _(u"自定义插件测试")
    code = 'test_custom'
    bound_service = TestCustomService
    embedded_form = True
    form = """
    (function(){
        $.atoms.test_custom = [
            {
                tag_code: "test_input",
                type: "input",
                attrs: {
                    name: gettext("参数1"),
                    placeholder: gettext("请输入字符串"),
                    hookable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
            },
            {
                tag_code: "test_textarea",
                type: "textarea",
                attrs: {
                    name: gettext("参数2"),
                    placeholder: gettext("多个用换行分隔"),
                    hookable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
            },
            {
                tag_code: "test_radio",
                type: "radio",
                attrs: {
                    name: gettext("参数3"),
                    items: [
                        {value: "1", name: gettext("选项1")},
                        {value: "2", name: gettext("选项2")},
                        {value: "3", name: gettext("选项3")}
                    ],
                    default: "1",
                    hookable: true,
                    validation: [
                        {
                            type: "required"
                        }
                    ]
                }
            }
        ]
    })();
    """