FROM bmat_webbase

ADD build/webpack/entrypoint.sh \
    $HOME/bin/

RUN chown -R web:web $HOME

USER $USER
VOLUME ["${HOME}/instance"]
ENTRYPOINT ["entrypoint.sh"]
CMD ["run"]