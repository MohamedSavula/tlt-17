# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Project Type'

    name = fields.Char(required=True)


class ProjectLocation(models.Model):
    _name = 'project.location'
    _description = 'Project Location'

    name = fields.Char(required=True)


class ProjectProjectInherit(models.Model):
    _inherit = 'project.project'

    project_type_id = fields.Many2one(comodel_name="project.type")
    project_location_id = fields.Many2one(comodel_name="project.location")
