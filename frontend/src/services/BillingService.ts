/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BillingPeriod } from '../models/BillingPeriod';
import type { BillingSearchResponse } from '../models/BillingSearchResponse';
import type { SearchOrder } from '../models/SearchOrder';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class BillingService {

    /**
     * Get Billing
     * Get a list of billing period summaries filtered by query.
     * @param period
     * @param iaas
     * @param account
     * @param page
     * @param perPage
     * @param sort
     * @param order
     * @returns BillingSearchResponse Successful Response
     * @throws ApiError
     */
    public static getBilling(
        period: string,
        iaas?: string,
        account?: string,
        page?: number,
        perPage: number = 20,
        sort?: string,
        order?: SearchOrder,
    ): CancelablePromise<BillingSearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/billing',
            query: {
                'period': period,
                'iaas': iaas,
                'account': account,
                'page': page,
                'per_page': perPage,
                'sort': sort,
                'order': order,
            },
            errors: {
                401: `Unauthorized`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Export Billing
     * Export billing periods as a spreadsheet.
     * @param template
     * @param period Billing period, defaults to current
     * @returns any Successful Response
     * @throws ApiError
     */
    public static exportBilling(
        template: string = 'default',
        period?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/billing/export',
            query: {
                'template': template,
                'period': period,
            },
            errors: {
                401: `Unauthorized`,
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Periods
     * Get a list of billing periods.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getPeriods(): CancelablePromise<Array<string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/billing/periods',
            errors: {
                401: `Unauthorized`,
            },
        });
    }

    /**
     * Get Billing Period
     * Get a billing period by id.
     * @param id
     * @returns BillingPeriod Successful Response
     * @throws ApiError
     */
    public static getBillingPeriod(
        id: number,
    ): CancelablePromise<BillingPeriod> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/billing/{id}',
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