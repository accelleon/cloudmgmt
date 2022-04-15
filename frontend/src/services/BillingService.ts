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
     * @param iaas
     * @param account
     * @param startDate
     * @param endDate
     * @param page
     * @param perPage
     * @param sort
     * @param order
     * @returns BillingSearchResponse Successful Response
     * @throws ApiError
     */
    public static getBilling(
        iaas?: string,
        account?: string,
        startDate?: string,
        endDate?: string,
        page?: number,
        perPage: number = 20,
        sort?: string,
        order?: SearchOrder,
    ): CancelablePromise<BillingSearchResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/billing',
            query: {
                'iaas': iaas,
                'account': account,
                'start_date': startDate,
                'end_date': endDate,
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