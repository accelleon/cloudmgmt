/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthRequest } from '../models/AuthRequest';
import type { AuthResponseOk } from '../models/AuthResponseOk';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class LoginService {
  /**
   * Login
   * @param requestBody
   * @returns AuthResponseOk Successful Response
   * @throws ApiError
   */
  public static login(
    requestBody: AuthRequest
  ): CancelablePromise<AuthResponseOk> {
    return __request(OpenAPI, {
      method: 'POST',
      url: '/api/v1/login',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        401: `Unauthorized`,
        403: `Forbidden`,
        422: `Validation Error`,
      },
    });
  }
}
