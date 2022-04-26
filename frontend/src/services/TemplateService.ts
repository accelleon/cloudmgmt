/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateTemplate } from '../models/CreateTemplate';
import type { Template } from '../models/Template';
import type { UpdateTemplate } from '../models/UpdateTemplate';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class TemplateService {

    /**
     * Get Templates
     * Get a list of templates.
     * @param custom
     * @returns Template Successful Response
     * @throws ApiError
     */
    public static getTemplates(
        custom: boolean = false,
    ): CancelablePromise<Array<Template>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/template',
            query: {
                'custom': custom,
            },
            errors: {
                401: `Unauthorized`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Template
     * Create a template.
     * @param requestBody
     * @returns Template Successful Response
     * @throws ApiError
     */
    public static createTemplate(
        requestBody: CreateTemplate,
    ): CancelablePromise<Template> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/template',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                409: `Conflict`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Template
     * Get a template by id.
     * @param id
     * @returns Template Successful Response
     * @throws ApiError
     */
    public static getTemplate(
        id: number,
    ): CancelablePromise<Template> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/template/{id}',
            path: {
                'id': id,
            },
            errors: {
                401: `Unauthorized`,
                404: `Not Found`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Template
     * Update a template.
     * @param id
     * @param requestBody
     * @returns Template Successful Response
     * @throws ApiError
     */
    public static updateTemplate(
        id: number,
        requestBody: UpdateTemplate,
    ): CancelablePromise<Template> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/template/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                404: `Not Found`,
                409: `Conflict`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Template
     * Delete a template.
     * @param id
     * @returns void
     * @throws ApiError
     */
    public static deleteTemplate(
        id: number,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/template/{id}',
            path: {
                'id': id,
            },
            errors: {
                401: `Unauthorized`,
                404: `Not Found`,
                422: `Validation Error`,
            },
        });
    }

}